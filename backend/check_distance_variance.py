import hashlib, random
from cortex import CortexClient

def make_vector(prompt, vibe):
    prompt_bytes = (prompt.lower().strip() + str(vibe)).encode()
    seed = int(hashlib.md5(prompt_bytes).hexdigest(), 16) % (2**31)
    random.seed(seed)
    return [random.uniform(-150.0, 150.0) for _ in range(512)]

prompts = [
    ("yacht rock to slow song", 30),
    ("heavy metal to classical", 30),
    ("jazz club late night", 80),
]

with CortexClient("localhost:50051") as client:
    for prompt, vibe in prompts:
        vec = make_vector(prompt, vibe)
        print(f"\nFirst 5 vals of vector for '{prompt}': {vec[:5]}")
        results = client.search("track_embeddings", query=vec, top_k=3)
        for r in results:
            _, payload = client.get("track_embeddings", r.id)
            title = payload.get("title") if payload else "?"
            print(f"  {title} (score={r.score:.2f})")
