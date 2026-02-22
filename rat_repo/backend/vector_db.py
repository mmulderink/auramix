"""Vector database client with Actian VectorAI + in-memory fallback."""

import os
import json
import math
from typing import Optional

import httpx
from google import genai

from models import ScamMessage

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SEED_SCAMS_PATH = "/Users/mm/Desktop/gt_hack/v3/data/seed_scams.json"


def embed_text(text: str) -> list[float]:
    """Embed text using Gemini text-embedding-004.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    result = client.models.embed_content(model="text-embedding-004", contents=text)
    return result.embeddings[0].values


class InMemoryFallback:
    """In-memory vector store using keyword overlap scoring when Actian is unavailable."""

    def __init__(self):
        self.collections: dict[str, dict[str, dict]] = {}

    def create_collection(self, name: str, dimension: int = 768):
        if name not in self.collections:
            self.collections[name] = {}

    def upsert(self, collection: str, doc_id: str, vector: list[float], metadata: dict):
        if collection not in self.collections:
            self.collections[collection] = {}
        self.collections[collection][doc_id] = {
            "vector": vector,
            "metadata": metadata,
        }

    def search(self, collection: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        if collection not in self.collections:
            return []

        results = []
        for doc_id, doc in self.collections[collection].items():
            score = self._cosine_similarity(query_vector, doc["vector"])
            results.append({
                "id": doc_id,
                "score": score,
                "metadata": doc["metadata"],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_stats(self, collection: str) -> dict:
        if collection not in self.collections:
            return {"collection": collection, "count": 0, "exists": False}
        return {
            "collection": collection,
            "count": len(self.collections[collection]),
            "exists": True,
        }

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class VectorDB:
    """Actian VectorAI DB client with REST API calls."""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("ACTIAN_URL", "http://localhost:8765")
        self.client = httpx.AsyncClient(base_url=self.url, timeout=10.0)

    async def create_collection(self, name: str, dimension: int = 768):
        try:
            response = await self.client.post(
                "/collections",
                json={"name": name, "dimension": dimension},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[vector_db] Failed to create collection: {e}")
            return None

    async def upsert(self, collection: str, doc_id: str, vector: list[float], metadata: dict):
        try:
            response = await self.client.post(
                f"/collections/{collection}/upsert",
                json={
                    "id": doc_id,
                    "vector": vector,
                    "metadata": metadata,
                },
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[vector_db] Failed to upsert: {e}")
            return None

    async def search(self, collection: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        try:
            response = await self.client.post(
                f"/collections/{collection}/search",
                json={
                    "vector": query_vector,
                    "top_k": top_k,
                },
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"[vector_db] Search failed: {e}")
            return []

    async def get_stats(self, collection: str) -> dict:
        try:
            response = await self.client.get(f"/collections/{collection}/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[vector_db] Stats failed: {e}")
            return {"collection": collection, "count": 0, "exists": False}

    async def close(self):
        await self.client.aclose()


class VectorStore:
    """Auto-detecting vector store that tries Actian first, then falls back to in-memory."""

    def __init__(self):
        self.actian_url = os.getenv("ACTIAN_URL", "http://localhost:8765")
        self.actian: Optional[VectorDB] = None
        self.fallback: InMemoryFallback = InMemoryFallback()
        self.using_actian: bool = False
        self._initialized: bool = False

    async def initialize(self):
        """Try to connect to Actian. Fall back to in-memory if unavailable."""
        if self._initialized:
            return

        try:
            self.actian = VectorDB(self.actian_url)
            stats = await self.actian.get_stats("test_connection")
            self.using_actian = True
            print("[vector_db] Connected to Actian VectorAI DB")
        except Exception as e:
            print(f"[vector_db] Actian unavailable ({e}), using in-memory fallback")
            self.using_actian = False
            if self.actian:
                await self.actian.close()
                self.actian = None

        self._initialized = True

    async def create_collection(self, name: str, dimension: int = 768):
        if self.using_actian and self.actian:
            return await self.actian.create_collection(name, dimension)
        else:
            return self.fallback.create_collection(name, dimension)

    async def upsert(self, collection: str, doc_id: str, vector: list[float], metadata: dict):
        if self.using_actian and self.actian:
            return await self.actian.upsert(collection, doc_id, vector, metadata)
        else:
            return self.fallback.upsert(collection, doc_id, vector, metadata)

    async def search(self, collection: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        if self.using_actian and self.actian:
            return await self.actian.search(collection, query_vector, top_k)
        else:
            return self.fallback.search(collection, query_vector, top_k)

    async def get_stats(self, collection: str) -> dict:
        if self.using_actian and self.actian:
            return await self.actian.get_stats(collection)
        else:
            return self.fallback.get_stats(collection)

    async def close(self):
        if self.actian:
            await self.actian.close()


# Module-level store instance
vector_store = VectorStore()


async def seed_scam_corpus():
    """Load seed scams, embed them, and upsert into the 'scam_corpus' collection."""
    await vector_store.initialize()
    await vector_store.create_collection("scam_corpus", dimension=768)

    # Load seed scams
    seed_scams = []
    try:
        with open(SEED_SCAMS_PATH, "r") as f:
            seed_scams = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Use the built-in fallback scams from scam_engine
        from scam_engine import _get_builtin_seed_scams
        seed_scams = _get_builtin_seed_scams()

    for i, scam in enumerate(seed_scams):
        text = f"{scam.get('sender', '')} {scam.get('subject', '')} {scam.get('content', '')}"
        try:
            vector = embed_text(text)
            metadata = {
                "sender": scam.get("sender", ""),
                "subject": scam.get("subject", ""),
                "is_scam": scam.get("is_scam", False),
                "scam_type": scam.get("scam_type", ""),
                "tactics": json.dumps(scam.get("tactics", [])),
                "red_flags": json.dumps(scam.get("red_flags", [])),
                "severity": scam.get("severity", 5),
            }
            await vector_store.upsert("scam_corpus", f"seed_{i}", vector, metadata)
        except Exception as e:
            print(f"[vector_db] Failed to embed/upsert seed scam {i}: {e}")

    stats = await vector_store.get_stats("scam_corpus")
    print(f"[vector_db] Seeded scam corpus: {stats}")


async def search_similar_scams(query: str, top_k: int = 5) -> list[dict]:
    """Search for scams similar to the given query text.

    Args:
        query: The text to search for.
        top_k: Number of results to return.

    Returns:
        List of matches with scores and metadata.
    """
    await vector_store.initialize()
    try:
        query_vector = embed_text(query)
        results = await vector_store.search("scam_corpus", query_vector, top_k)

        # Parse JSON fields in metadata
        for result in results:
            meta = result.get("metadata", {})
            for field in ("tactics", "red_flags"):
                if isinstance(meta.get(field), str):
                    try:
                        meta[field] = json.loads(meta[field])
                    except json.JSONDecodeError:
                        pass

        return results
    except Exception as e:
        print(f"[vector_db] Search failed: {e}")
        return []
