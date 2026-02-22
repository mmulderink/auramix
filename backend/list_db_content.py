import json
from cortex import CortexClient

with CortexClient("localhost:50051") as client:
    if client.has_collection("track_embeddings"):
        results = client.search("track_embeddings", query=[0]*512, top_k=50)
        print("Tracks:")
        for r in results:
            title = r.payload.get('title') if r.payload else 'Missing Payload'
            print(f"- {title} (ID: {r.id}, Score: {r.score})")
    else:
        print("No collection.")
