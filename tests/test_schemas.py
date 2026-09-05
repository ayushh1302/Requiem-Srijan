from backend.models.schemas import (
    ClauseItem,
    ClauseAnalysisItem,
    RiskLevel,
    FairnessScoreResult,
    MissingProtectionItem,
    ImportanceLevel
)

def test_clause_item_schema():
    c = ClauseItem(
        id="clause_1",
        number="1",
        title="Termination",
        category="termination",
        original_text="The agreement may be terminated by either party."
    )
    assert c.id == "clause_1"
    assert c.category == "termination"

def test_clause_analysis_schema():
    a = ClauseAnalysisItem(
        clause_id="clause_1",
        plain_english="Either side can cancel with notice.",
        risk_level=RiskLevel.GREEN,
        risk_reason="Balanced notice",
        key_concern="Giving notice on time",
        suggested_alternative=None,
        recommended_user_action="Follow written notice format",
        confidence=0.95
    )
    assert a.risk_level == RiskLevel.GREEN
    assert a.confidence >= 0.85
