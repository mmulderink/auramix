from cortex import CortexClient
import time

max_retries = 3
with CortexClient("localhost:50051") as client:
    for attempt in range(max_retries):
        try:
            if client.has_collection("track_embeddings"):
                client.delete_collection("track_embeddings")
                print("Successfully wiped Actian Vector DB!")
            else:
                print("No collection found. Nothing to wipe.")
            break
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            time.sleep(1)
