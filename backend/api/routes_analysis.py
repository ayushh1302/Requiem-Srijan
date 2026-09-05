from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from backend.models.schemas import ContractAnalysisResponse
from backend.storage.database import (
    get_raw_contract,
    save_full_analysis,
    get_full_analysis
)
from backend.services.llm_service import LLMService
from backend.services.scoring_service import (
    detect_contract_type,
    evaluate_missing_protections,
    calculate_fairness_score
)
from backend.services.rag_service import RAGService

router = APIRouter(tags=["Analysis"])

llm_service = LLMService()
rag_service = RAGService()

class AnalyzeRequest(BaseModel):
    session_id: str
    contract_type: Optional[str] = None

@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: AnalyzeRequest):
    """
    Executes end-to-end clause segmentation, risk analysis, fairness scoring, missing protections detection, and ChromaDB indexing.
    """
    session_id = request.session_id
    raw_contract = get_raw_contract(session_id)

    if not raw_contract:
        raise HTTPException(status_code=404, detail="No contract found for this session. Please upload a document first.")

    raw_text = raw_contract["raw_text"]
    filename = raw_contract["filename"]
    page_count = raw_contract["page_count"]
    char_count = raw_contract["char_count"]
    file_type = filename.split(".")[-1] if "." in filename else "pdf"

    # Determine contract type
    contract_type = request.contract_type or detect_contract_type(raw_text, filename)

    try:
        # 1. Clause Segmentation
        clauses = llm_service.segment_clauses(raw_text, filename)

        # 2. Missing Protections Evaluation
        missing_protections = evaluate_missing_protections(contract_type, raw_text)

        # 3. Clause Risk & Plain-English Analysis
        analysis_items = llm_service.analyze_clauses(clauses, contract_type)

        # 4. Fairness Scoring
        fairness_score = calculate_fairness_score(analysis_items, missing_protections, contract_type)

        # 5. ChromaDB Indexing for RAG
        rag_service.index_clauses(session_id, clauses)

        # 6. Save Full Analysis to SQLite
        save_full_analysis(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            contract_type=contract_type,
            clauses=clauses,
            analysis=analysis_items,
            fairness=fairness_score,
            missing_protections=missing_protections,
            page_count=page_count,
            char_count=char_count
        )

        return ContractAnalysisResponse(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            contract_type=contract_type,
            page_count=page_count,
            char_count=char_count,
            fairness=fairness_score,
            clauses=clauses,
            analysis=analysis_items,
            missing_protections=missing_protections,
            executive_summary=fairness_score.summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@router.get("/analysis/{session_id}", response_model=ContractAnalysisResponse)
async def get_analysis_by_session(session_id: str):
    """
    Retrieves previously computed contract analysis for a session.
    """
    analysis = get_full_analysis(session_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this session ID.")
    return analysis
