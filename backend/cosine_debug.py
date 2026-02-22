import hashlib, random
from cortex import CortexClient

def make_vector(prompt, vibe):
    b = (prompt.lower().strip() + str(vibe)).encode()
    seed = int(hashlib.md5(b).hexdigest(), 16) % (2**31)
    random.seed(seed)
    return [random.uniform(-150.0, 150.0) for _ in range(512)]

with CortexClient("localhost:50051") as client:
    for prompt, vibe in [("yacht rock", 30), ("heavy metal", 30), ("jazz", 80)]:
        vec = make_vector(prompt, vibe)
        results = client.search("track_embeddings", query=vec, top_k=5)
        print(f"\n'{prompt}' vibe={vibe}:")
        for r in results:
            _, pl = client.get("track_embeddings", r.id)
            print(f"  {pl.get('title') if pl else '?'} score={r.score:.6f}")
