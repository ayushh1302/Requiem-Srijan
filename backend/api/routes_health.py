from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.utils.config import APP_NAME, APP_VERSION, LLM_PROVIDER, DEMO_MODE, CHROMA_DIR

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    chroma_status = "ready" if CHROMA_DIR.exists() else "not_initialized"
    return HealthResponse(
        status="healthy",
        app_name=APP_NAME,
        version=APP_VERSION,
        llm_provider=LLM_PROVIDER,
        demo_mode=DEMO_MODE,
        chroma_status=chroma_status
    )
