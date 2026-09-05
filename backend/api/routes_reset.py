from fastapi import APIRouter
from backend.models.schemas import ResetResponse
from backend.storage.database import clear_session
from backend.services.rag_service import RAGService

router = APIRouter(tags=["Reset"])
rag_service = RAGService()

@router.post("/reset/{session_id}", response_model=ResetResponse)
async def reset_session(session_id: str):
    """
    Clears all stored data, vectors, and chat history for the specified session.
    """
    clear_session(session_id)
    rag_service.clear_session(session_id)

    return ResetResponse(
        status="success",
        session_id=session_id,
        message=f"Session {session_id} has been completely reset."
    )
