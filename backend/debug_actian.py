from cortex import CortexClient

with CortexClient("localhost:50051") as client:
    has = client.has_collection("track_embeddings")
    print(f"Has collection: {has}")
    if has:
        count = client.count("track_embeddings")
        print(f"Vector count: {count}")
        results = client.search("track_embeddings", query=[0.5]*512, top_k=5)
        print(f"Search results count: {len(results)}")
        for r in results:
            _, payload = client.get("track_embeddings", r.id)
            print(f"ID={r.id}, Score={r.score:.2f}, Payload={payload}")
