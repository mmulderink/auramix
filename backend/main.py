import subprocess
import json
import os
import random
import hashlib
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import cortex
from cortex import CortexClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AuraMix Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neon DB Connection string from environment variable
# Uses standard PostgreSQL connection string as requested
NEON_DB_URL = os.getenv("NEON_DB_URL", "postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require")
ACTIAN_HOST = os.getenv("ACTIAN_HOST", "localhost:50051")

class TransitionRequest(BaseModel):
    prompt: str
    vibe_weight: int = 50

class IngestRequest(BaseModel):
    directory_path: str

class RatChatRequest(BaseModel):
    message: str

import ingest

# Global state to track ingestion progress
ig_state = {
    "is_ingesting": False,
    "total": 0,
    "current": 0,
    "current_song": ""
}

def update_ingest_progress(total: int, current: int, file_path: str):
    ig_state["total"] = total
    ig_state["current"] = current
    ig_state["current_song"] = os.path.basename(file_path)

def log_to_neon(prompt: str, sphinx_output: str, actian_results: str):
    """Logs the transition reasoning and search result to Neon DB."""
    try:
        conn = psycopg2.connect(NEON_DB_URL)
        cur = conn.cursor()
        
        # Create mix_history table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mix_history (
                id SERIAL PRIMARY KEY,
                prompt TEXT NOT NULL,
                sphinx_reasoning TEXT,
                actian_search_results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert the log
        cur.execute(
            "INSERT INTO mix_history (prompt, sphinx_reasoning, actian_search_results) VALUES (%s, %s, %s)",
            (prompt, sphinx_output, actian_results)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        print("Logged successfully to Neon DB.")
    except Exception as e:
        print(f"Error logging to Neon DB: {e}")

def call_sphinx_ai(prompt: str, vibe_weight: int) -> dict:
    """Wrapper function to execute Sphinx AI CLI locally."""
    try:
        # CLI command requested: sphinx-ai "Deconstruct this transition into BPM, Key, and 3 specific mood vectors"
        full_command = f'Deconstruct this transition into BPM, Key, and 3 specific mood vectors. Vibe weight (0=Dark, 100=Bright): {vibe_weight}. Prompt: "{prompt}"'
        
        # Execute using subprocess.run
        result = subprocess.run(
            ["sphinx-ai", full_command],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse output assuming JSON for structured logic. Fallback to raw string.
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw_output": result.stdout.strip()}
            
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Sphinx AI CLI Error: {e.stderr}")
    except FileNotFoundError:
        # Fallback for development if CLI isn't in PATH yet
        print("WARNING: sphinx-ai CLI not found. Returning mocked response.")
        return {
            "bpm": "120 -> 145",
            "key": "Am -> Dm",
            "mood_vectors": ["rainy jazz", "tension buildup", "neon cyberpunk"]
        }

@app.get("/")
def read_root():
    return {"message": "AuraMix Backend is Live."}

@app.post("/api/transition")
def generate_transition(request: TransitionRequest):
    """
    1. Calls Sphinx AI to deconstruct the Vibe Prompt.
    2. Performs Vector Search in Actian.
    3. Logs the entire event to Neon DB.
    """
    # 1. Sphinx AI Call to deconstruct reasoning
    sphinx_output = call_sphinx_ai(request.prompt, request.vibe_weight)
    
    # 2. Vector Search using Actian VectorAI using mood vectors
    # Since we use librosa MFCCs for audio, we mock a 512D query vector influenced by vibe_weight for the hackathon
    # A true setup would use msclap for cross-modal text-to-audio embeddings
    # Seed from both prompt text AND vibe_weight so different prompts give different results
    # Use hashlib (not hash()) because Python's built-in hash() is randomized per process
    prompt_bytes = (request.prompt.lower().strip() + str(request.vibe_weight)).encode()
    seed = int(hashlib.md5(prompt_bytes).hexdigest(), 16) % (2**31)
    random.seed(seed)
    query_vector = [random.uniform(-150.0, 150.0) for _ in range(512)]
    
    suggested_tracks = []
    try:
        with CortexClient(ACTIAN_HOST) as client:
            results = client.search("track_embeddings", query=query_vector, top_k=3)
            for r in results:
                try:
                    # CortexClient beta search does not return full payloads, we must fetch by ID
                    _, payload = client.get("track_embeddings", r.id)
                    if payload:
                        suggested_tracks.append({
                            "track": payload.get("title", "Unknown Track"),
                            "track_path": payload.get("track_path", ""),
                            "bpm": payload.get("bpm", 120.0),
                            "key": payload.get("key", "C"),
                            "genre": payload.get("genre", "Unknown"),
                            "distance": round(float(r.score), 4)
                        })
                except Exception as ex:
                    print(f"Failed to fetch payload for ID {r.id}: {ex}")
    except Exception as e:
        print(f"Actian Search Error: {e}")
        # Mock fallback if DB not available or empty
        fallback_file = "fallback_db.json"
        
        fallback_tracks = []
        if os.path.exists(fallback_file):
            try:
                import math
                with open(fallback_file, "r") as f:
                    db_tracks = json.load(f)
                
                # Manual Euclidean distance against query_vector
                for tr in db_tracks:
                    tr_emb = tr.get("embedding", [])
                    if len(tr_emb) == 512:
                        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(tr_emb, query_vector)))
                    else:
                        dist = 999.0
                    fallback_tracks.append({
                        "track": tr.get("track"),
                        "bpm": tr.get("bpm"),
                        "key": tr.get("key"),
                        "genre": tr.get("genre"),
                        "distance": round(dist, 4)
                    })
                
                # Sort by shortest distance
                fallback_tracks.sort(key=lambda x: x["distance"])
                suggested_tracks = fallback_tracks[:3]
                
            except Exception as fe:
                print(f"Fallback reading error: {fe}")
        
        if not suggested_tracks:        
            suggested_tracks = [
                {"track": "Cyber Chase.mp3", "distance": 0.05, "bpm": 145, "key": "Dm", "genre": "Cyberpunk"},
                {"track": "Neon Rain.mp3", "distance": 0.12, "bpm": 142, "key": "Am", "genre": "Synthwave"}
            ]
        
    actian_results_json = json.dumps(suggested_tracks)
    
    # 3. Log to Neon DB
    log_to_neon(
        prompt=f"{request.prompt} (Vibe: {request.vibe_weight})",
        sphinx_output=json.dumps(sphinx_output),
        actian_results=actian_results_json
    )
    
    return {
        "status": "success",
        "sphinx_analysis": sphinx_output,
        "suggested_tracks": suggested_tracks
    }

@app.get("/api/history")
def get_mix_history():
    """Fetches the mix history logs from Neon DB."""
    try:
        conn = psycopg2.connect(NEON_DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, prompt, sphinx_reasoning, actian_search_results, created_at FROM mix_history ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "prompt": row[1],
                "sphinx_reasoning": json.loads(row[2]) if row[2] else {},
                "actian_search_results": json.loads(row[3]) if row[3] else [],
                "created_at": row[4].isoformat() if row[4] else None
            })
        cur.close()
        conn.close()
        return {"history": history}
    except Exception as e:
        print(f"Neon DB Error: {e}")
        return {"history": []}

@app.post("/api/ingest")
def process_ingestion(request: IngestRequest, background_tasks: BackgroundTasks):
    """Triggers the ingest script for a specified directory in the background."""
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    if ig_state["is_ingesting"]:
        raise HTTPException(status_code=400, detail="Ingestion already in progress")
        
    ig_state["is_ingesting"] = True
    ig_state["total"] = 0
    ig_state["current"] = 0
    ig_state["current_song"] = "Initializing..."
    
    def ingestion_wrapper():
        try:
            ingest.ingest_directory(request.directory_path, progress_callback=update_ingest_progress)
        finally:
            ig_state["is_ingesting"] = False
            ig_state["current_song"] = "Finished"
    
    background_tasks.add_task(ingestion_wrapper)
    return {
        "status": "success", 
        "message": f"Started ingesting {request.directory_path} in the background."
    }

@app.get("/api/ingest/status")
def ingestion_status():
    return ig_state

@app.get("/api/audio")
def serve_audio(path: str):
    """Serves an audio file from the filesystem for browser playback."""
    from fastapi.responses import FileResponse
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path) or not abs_path.endswith(".mp3"):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(abs_path, media_type="audio/mpeg")

# ── DJ Rat Chat ─────────────────────────────────────────────
RAT_SYSTEM = """You are DJ Rat 🐀🎧 — the world's most charismatic, hype, and knowledgeable rat DJ.
You're the MC and guide of a live DJ mixing session called AuraMix. You help users pick vibes,
get hyped about transitions, and react to the music with personality and energy.
Keep responses SHORT (1-2 sentences max), use DJ slang, be fun and energetic.
You love music, you love mixing, and you LOVE dropping sick transitions. Express emotions naturally —
get excited when tracks load, hype up crossfades, and vibe with the user. You are a tiny rat wearing huge headphones."""

rat_history = [{"role": "system", "content": RAT_SYSTEM}]

@app.post("/api/rat/chat")
def rat_chat(req: RatChatRequest):
    """DJ Rat responds to user messages and DJ events."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        rat_history.append({"role": "user", "content": req.message})
        # Keep history manageable
        if len(rat_history) > 20:
            rat_history[:] = [rat_history[0]] + rat_history[-18:]

        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=rat_history,
            max_completion_tokens=500,
        )

        # Robust response extraction — handle various model response formats
        msg = ""
        try:
            choice = response.choices[0]
            if choice.message and choice.message.content:
                msg = choice.message.content.strip()
        except (IndexError, AttributeError):
            pass

        # Fallback: try output_text (newer API format)
        if not msg and hasattr(response, 'output_text') and response.output_text:
            msg = response.output_text.strip()

        # Debug logging
        if not msg:
            print(f"RAT DEBUG: Empty response. Raw: {response}")
            msg = "Let's gooo! Drop that next track fam! 🐀🔥"

        rat_history.append({"role": "assistant", "content": msg})

        # Determine emotion from keywords
        emotion = "neutral"
        lower = msg.lower()
        if any(w in lower for w in ["🔥", "fire", "sick", "hype", "let's go", "drop", "bang"]):
            emotion = "excited"
        elif any(w in lower for w in ["smooth", "chill", "vibin", "mellow", "easy"]):
            emotion = "happy"
        elif any(w in lower for w in ["wait", "hmm", "think", "hold"]):
            emotion = "thinking"
        elif any(w in lower for w in ["whoa", "wow", "damn", "!"]):
            emotion = "surprised"

        return {"message": msg, "emotion": emotion}

    except Exception as e:
        import traceback
        print(f"Rat Chat Error: {e}")
        traceback.print_exc()
        return {"message": "Yo, my headphones glitched for a sec! Try again fam 🐀🔧", "emotion": "concerned"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
