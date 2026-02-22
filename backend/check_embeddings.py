import json
from cortex import CortexClient

with CortexClient("localhost:50051") as client:
    # Try 3 very different query vectors and see what comes back
    prompts_vecs = [
        ("yacht rock", [150.0] * 512),
        ("heavy metal", [-150.0] * 512),
        ("jazz chill", [0.0] * 512),
    ]
    for name, vec in prompts_vecs:
        results = client.search("track_embeddings", query=vec, top_k=3)
        ids = [r.id for r in results]
        titles = []
        for id_ in ids:
            _, payload = client.get("track_embeddings", id_)
            titles.append(payload.get("title") if payload else "N/A")
        print(f"{name}: {titles}")
