import os
import glob
import librosa
import numpy as np
import psycopg2 
import cortex
from cortex import CortexClient, DistanceMetric

# Connection using VectorAI's native Python Client (cortex) over gRPC
ACTIAN_HOST = os.getenv("ACTIAN_HOST", "localhost:50051")

def extract_key(y, sr):
    """Basic heuristic to extract musical key from chroma features."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_sum = np.sum(chroma, axis=1)
    note_idx = np.argmax(chroma_sum)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes[note_idx]

def extract_metadata_and_embedding(file_path: str) -> dict:
    """
    Generates a 512-dimension embedding and extracts metadata using librosa.
    """
    try:
        # Load first 30 seconds of audio, resampled to 22050 Hz
        y, sr = librosa.load(file_path, duration=30.0) 
        
        # Extract metadata
        title = os.path.basename(file_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0] if isinstance(tempo, np.ndarray) else tempo)
        key = extract_key(y, sr)
        # BPM-based genre heuristic
        if bpm < 70:
            genre = "Ballad / Slow"
        elif bpm < 100:
            genre = "R&B / Soul"
        elif bpm < 120:
            genre = "Rock / Pop"
        elif bpm < 140:
            genre = "Dance / Electronic"
        else:
            genre = "Uptempo / EDM"
        
        # Extract MFCCs (Mel-frequency cepstral coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        
        # Flatten and pad/truncate to exactly 512 dimensions
        flattened = mfcc.flatten()
        if len(flattened) >= 512:
            embedding = flattened[:512]
        else:
            embedding = np.pad(flattened, (0, 512 - len(flattened)), mode='constant')
            
        return {
            "embedding": embedding.tolist(),
            "title": title,
            "bpm": bpm,
            "key": key,
            "genre": genre
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            "embedding": [0.0] * 512,
            "title": os.path.basename(file_path),
            "bpm": 120.0,
            "key": "C",
            "genre": "Unknown"
        }

def push_to_actian_batch(all_tracks: list):
    """Drops and recreates the collection, then batch-upserts all tracks with sequential IDs."""
    try:
        with CortexClient(ACTIAN_HOST) as client:
            # Always start fresh to avoid duplicate ID collisions
            if client.has_collection("track_embeddings"):
                client.delete_collection("track_embeddings")
                print("Dropped existing track_embeddings collection.")
            
            client.create_collection(
                name="track_embeddings",
                dimension=512,
                distance_metric=DistanceMetric.COSINE,
            )
            print(f"Created fresh track_embeddings collection.")

            # Use sequential IDs (0, 1, 2, ...) — no hash collisions ever
            ids = list(range(len(all_tracks)))
            vectors = [t["embedding"] for t in all_tracks]
            payloads = [
                {
                    "track_path": t["file_path"],
                    "title": t["title"],
                    "bpm": t["bpm"],
                    "key": t["key"],
                    "genre": t["genre"],
                }
                for t in all_tracks
            ]
            client.batch_upsert("track_embeddings", ids, vectors, payloads)
            print(f"Batch upserted {len(all_tracks)} tracks into Actian VectorAI.")
            return True
    except Exception as e:
        print(f"Actian Batch Error: {e}")
        return False


def save_to_fallback(all_tracks: list):
    """Save all tracks to local fallback_db.json, filtering out zero-vector test tracks."""
    import json
    clean = [
        {
            "track": t["title"],
            "bpm": t["bpm"],
            "key": t["key"],
            "genre": t["genre"],
            "embedding": t["embedding"],
        }
        for t in all_tracks
        if any(v != 0.0 for v in t["embedding"])
    ]
    with open("fallback_db.json", "w") as f:
        json.dump(clean, f)
    print(f"Saved {len(clean)} tracks to fallback_db.json")


def _old_push_per_file_unused(file_path: str, data: dict):
    """Kept for reference only - do not call directly."""
    # Save to local fallback DB for Hackathon usage if Actian is unreachable
    fallback_file = "fallback_db.json"
    import json
    if os.path.exists(fallback_file):
        try:
            with open(fallback_file, "r") as f:
                db = json.load(f)
        except:
            db = []
        else:
            db = []
            
        # Add or update the track
        existing = next((item for item in db if item["track"] == data["title"]), None)
        if not existing:
            db.append({
                "track": data["title"],
                "bpm": data["bpm"],
                "key": data["key"],
                "genre": data["genre"],
                "embedding": data["embedding"]
            })
        
        with open(fallback_file, "w") as f:
            json.dump(db, f)

import sys

def ingest_directory(directory_path: str, progress_callback=None):
    """
    Reads all MP3s in a directory and its subdirectories,
    extracts librosa 512D embeddings, and batch-pushes to Actian.
    Optionally reports progress back via progress_callback function.
    """
    mp3_files = glob.glob(os.path.join(directory_path, "**", "*.mp3"), recursive=True)
    total_files = len(mp3_files)
    print(f"Found {total_files} MP3 files in '{directory_path}'. Starting ingestion...")

    all_tracks = []
    for i, file_path in enumerate(mp3_files, 1):
        print(f"Processing ({i}/{total_files}): {os.path.basename(file_path)}")
        if progress_callback:
            progress_callback(total=total_files, current=i, file_path=file_path)

        data = extract_metadata_and_embedding(file_path)
        data["file_path"] = file_path
        all_tracks.append(data)

    print(f"Extracted all {len(all_tracks)} tracks. Uploading to Actian...")
    success = push_to_actian_batch(all_tracks)
    if not success:
        print("Actian upload failed. Saving to local fallback_db.json...")
        save_to_fallback(all_tracks)

    print("Ingestion complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample_dir = sys.argv[1]
    else:
        sample_dir = "./audio_samples"
        
    os.makedirs(sample_dir, exist_ok=True)
    
    mp3_files = glob.glob(os.path.join(sample_dir, "**", "*.mp3"), recursive=True)
    if not mp3_files:
        print(f"Please add some .mp3 files to '{sample_dir}' or pass a directory as an argument: python ingest.py /path/to/music")
    else:
        ingest_directory(sample_dir)
