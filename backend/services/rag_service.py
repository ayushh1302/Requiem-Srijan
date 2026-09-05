import chromadb
from typing import List, Optional
from backend.utils.config import CHROMA_DIR
from backend.models.schemas import ClauseItem, ChatResponse
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService

class RAGService:
    def __init__(self):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def _get_collection_name(self, session_id: str) -> str:
        # Chroma collection names must be 3-63 chars, alphanumeric, starts/ends with alphanumeric
        clean_id = "".join([c if c.isalnum() else "_" for c in session_id])
        return f"sess_{clean_id[:45]}"

    def index_clauses(self, session_id: str, clauses: List[ClauseItem]):
        """
        Indexes segmented clauses into ChromaDB for vector retrieval.
        """
        if not clauses:
            return

        col_name = self._get_collection_name(session_id)
        # Reset existing collection if present
        try:
            self.chroma_client.delete_collection(col_name)
        except Exception:
            pass

        collection = self.chroma_client.create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"}
        )

        texts = [f"{c.title} ({c.category}): {c.original_text}" for c in clauses]
        embeddings = self.embedding_service.get_embeddings(texts)
        ids = [f"{session_id}_{c.id}" for c in clauses]
        metadatas = [
            {
                "session_id": session_id,
                "clause_id": c.id,
                "number": c.number or "",
                "title": c.title,
                "category": c.category,
                "original_text": c.original_text
            }
            for c in clauses
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def retrieve_relevant_clauses(self, session_id: str, query: str, top_k: int = 3) -> List[ClauseItem]:
        """
        Retrieves the top_k most relevant clauses for a given question.
        """
        col_name = self._get_collection_name(session_id)
        try:
            collection = self.chroma_client.get_collection(col_name)
        except Exception:
            return []

        query_embedding = self.embedding_service.get_single_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )

        matched_clauses = []
        if results and "metadatas" in results and results["metadatas"]:
            for meta in results["metadatas"][0]:
                matched_clauses.append(
                    ClauseItem(
                        id=meta.get("clause_id", ""),
                        number=meta.get("number", ""),
                        title=meta.get("title", ""),
                        category=meta.get("category", "miscellaneous"),
                        original_text=meta.get("original_text", "")
                    )
                )

        return matched_clauses

    def answer_query(self, session_id: str, query: str) -> ChatResponse:
        """
        End-to-end RAG workflow: Retrieves relevant clauses and passes them to LLM for grounded answer.
        """
        retrieved = self.retrieve_relevant_clauses(session_id, query, top_k=3)
        return self.llm_service.answer_contract_question(query, retrieved)

    def clear_session(self, session_id: str):
        col_name = self._get_collection_name(session_id)
        try:
            self.chroma_client.delete_collection(col_name)
        except Exception:
            pass
