from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RiskLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class ImportanceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ContractType(str, Enum):
    RENTAL = "rental"
    EMPLOYMENT = "employment"
    FREELANCE = "freelance"
    SERVICE = "service"
    GENERIC = "generic"

class ClauseCategory(str, Enum):
    PAYMENT = "payment"
    TERMINATION = "termination"
    NOTICE = "notice"
    CONFIDENTIALITY = "confidentiality"
    LIABILITY = "liability"
    INDEMNITY = "indemnity"
    DISPUTE_RESOLUTION = "dispute_resolution"
    DEPOSIT = "deposit"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    NON_COMPETE = "non_compete"
    WORKING_HOURS = "working_hours"
    LEAVE = "leave"
    RENEWAL = "renewal"
    RENT = "rent"
    MAINTENANCE = "maintenance"
    PENALTIES = "penalties"
    OBLIGATIONS = "obligations"
    MISCELLANEOUS = "miscellaneous"

# ==========================================
# CLAUSE SCHEMAS
# ==========================================

class ClauseItem(BaseModel):
    id: str = Field(..., description="Unique clause identifier e.g. clause_1")
    number: Optional[str] = Field(None, description="Clause number or heading if present")
    title: str = Field(..., description="Clause title or summary headline")
    category: str = Field(default="miscellaneous", description="Clause legal domain category")
    original_text: str = Field(..., description="Verbatim text of the clause extracted from contract")

class ClauseSegmentationResult(BaseModel):
    clauses: List[ClauseItem] = Field(default_factory=list, description="List of segmented legal clauses")
    contract_type_hint: Optional[str] = Field(None, description="Inferred contract type")

class ClauseAnalysisItem(BaseModel):
    clause_id: str = Field(..., description="ID matching ClauseItem.id")
    plain_english: str = Field(..., description="Plain-English explanation at 8th-grade reading level")
    risk_level: RiskLevel = Field(..., description="GREEN (Safe), YELLOW (Caution), or RED (High Risk)")
    risk_reason: str = Field(..., description="Clear explanation of why this clause is scored at this risk level")
    key_concern: str = Field(..., description="The single biggest practical hazard or watch-out for the signer")
    suggested_alternative: Optional[str] = Field(None, description="Balanced, negotiation-ready alternative clause wording")
    recommended_user_action: str = Field(..., description="Concrete practical action the user should take before signing")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Confidence score between 0 and 1")

# ==========================================
# FAIRNESS SCORE & MISSING PROTECTIONS
# ==========================================

class FairnessScoreResult(BaseModel):
    fairness_score: int = Field(..., ge=0, le=100, description="Weighted contract fairness score from 0 to 100")
    fairness_label: str = Field(..., description="Fair (85-100), Mostly Fair (70-84), Needs Review (50-69), High Risk (0-49)")
    summary: str = Field(..., description="Overall executive summary of contract balance")
    green_count: int = Field(default=0)
    yellow_count: int = Field(default=0)
    red_count: int = Field(default=0)
    missing_count: int = Field(default=0)
    breakdown_notes: Optional[List[str]] = Field(default_factory=list)
    disclaimer: str = Field(default="This score is an AI-generated educational indicator, not a legal opinion.")

class MissingProtectionItem(BaseModel):
    name: str = Field(..., description="Name of the missing protection e.g. Deposit refund timeline")
    importance: ImportanceLevel = Field(default=ImportanceLevel.MEDIUM, description="HIGH, MEDIUM, or LOW")
    reason: str = Field(..., description="Why this protection is commonly included and why its absence matters")
    recommendation: Optional[str] = Field(None, description="Suggested clause or question to add to the agreement")

class MissingProtectionsResult(BaseModel):
    contract_type: str = Field(..., description="Identified contract type e.g. rental, employment, freelance")
    missing_protections: List[MissingProtectionItem] = Field(default_factory=list)

# ==========================================
# FULL CONTRACT ANALYSIS AGGREGATE
# ==========================================

class ContractAnalysisResponse(BaseModel):
    session_id: str
    filename: str
    file_type: str
    contract_type: str
    page_count: int = 1
    char_count: int = 0
    fairness: FairnessScoreResult
    clauses: List[ClauseItem]
    analysis: List[ClauseAnalysisItem]
    missing_protections: List[MissingProtectionItem]
    executive_summary: str
    created_at: Optional[str] = None

# ==========================================
# UPLOAD SCHEMAS
# ==========================================

class DocumentUploadResponse(BaseModel):
    session_id: str
    filename: str
    file_type: str
    page_count: int
    text_length: int
    char_count: int
    message: str

# ==========================================
# CHAT (RAG) SCHEMAS
# ==========================================

class SourceClause(BaseModel):
    clause_id: str
    title: str
    snippet: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    source_clauses: List[SourceClause] = Field(default_factory=list)
    grounded: bool = True
    confidence_note: Optional[str] = None

# ==========================================
# REPORT & SYSTEM SCHEMAS
# ==========================================

class ReportResponse(BaseModel):
    session_id: str
    filename: str
    pdf_path: str
    download_url: str
    message: str

class ResetResponse(BaseModel):
    status: str
    session_id: str
    message: str

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    llm_provider: str
    demo_mode: bool
    chroma_status: str
