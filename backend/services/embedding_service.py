import hashlib
import numpy as np
from typing import List, Optional
from backend.utils.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

class EmbeddingService:
    def __init__(self):
        self._openai_client = None
        self.use_openai = bool(OPENAI_API_KEY)

    def _get_client(self):
        if self._openai_client is None and OPENAI_API_KEY:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
        return self._openai_client

    def _generate_fallback_embedding(self, text: str, dim: int = 384) -> List[float]:
        """
        Generates a deterministic pseudo-semantic dense vector for offline/demo mode.
        Uses character n-grams and word hashing to preserve lexical similarity.
        """
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            pos = h % dim
            weight = 1.0 / (1.0 + 0.1 * i)
            vec[pos] += weight

        # Add 3-gram character features
        for j in range(len(text) - 2):
            gram = text[j:j+3].lower()
            h = int(hashlib.sha256(gram.encode()).hexdigest(), 16)
            pos = h % dim
            vec[pos] += 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a batch of text strings.
        """
        if not texts:
            return []

        if self.use_openai and OPENAI_API_KEY:
            try:
                client = self._get_client()
                response = client.embeddings.create(
                    model=OPENAI_EMBEDDING_MODEL,
                    input=texts
                )
                return [d.embedding for d in response.data]
            except Exception as e:
                print(f"[EmbeddingService] OpenAI embedding failed: {e}. Using deterministic local embedding.")

        return [self._generate_fallback_embedding(t) for t in texts]

    def get_single_embedding(self, text: str) -> List[float]:
        return self.get_embeddings([text])[0]
