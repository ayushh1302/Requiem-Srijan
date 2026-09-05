from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.rag_service import RAGService
from backend.storage.database import save_chat_message, get_full_analysis

router = APIRouter(tags=["Chat"])
rag_service = RAGService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_contract(request: ChatRequest):
    """
    RAG-powered conversational endpoint. Answers user questions strictly grounded on contract clauses.
    """
    session_id = request.session_id
    query = request.message.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    # Check if session exists
    analysis = get_full_analysis(session_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analyzed contract found for this session. Please analyze a contract first.")

    try:
        # Save user message
        save_chat_message(session_id=session_id, role="user", content=query)

        # Retrieve and generate grounded response
        response = rag_service.answer_query(session_id, query)

        # Save assistant message
        sources_dicts = [s.model_dump() for s in response.source_clauses]
        save_chat_message(
            session_id=session_id,
            role="assistant",
            content=response.answer,
            source_clauses=sources_dicts,
            grounded=response.grounded
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Chat error: {str(e)}")
