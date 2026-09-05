from backend.models.schemas import ClauseAnalysisItem, RiskLevel, MissingProtectionItem, ImportanceLevel
from backend.services.scoring_service import calculate_fairness_score

def test_fairness_score_all_green():
    items = [
        ClauseAnalysisItem(
            clause_id=f"c_{i}",
            plain_english="Safe term",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard",
            key_concern="None",
            suggested_alternative=None,
            recommended_user_action="Proceed",
            confidence=0.95
        )
        for i in range(5)
    ]
    res = calculate_fairness_score(items, [], "rental")
    assert res.fairness_score >= 90
    assert res.fairness_label == "Fair"
    assert res.green_count == 5
    assert res.red_count == 0

def test_fairness_score_with_red_and_missing():
    items = [
        ClauseAnalysisItem(
            clause_id="c_1",
            plain_english="Punitive eviction",
            risk_level=RiskLevel.RED,
            risk_reason="24hr eviction without notice",
            key_concern="Homelessness",
            suggested_alternative="30 days notice",
            recommended_user_action="Negotiate",
            confidence=0.98
        ),
        ClauseAnalysisItem(
            clause_id="c_2",
            plain_english="Deposit forfeiture",
            risk_level=RiskLevel.RED,
            risk_reason="Deposit seized for 1-day delay",
            key_concern="Loss of funds",
            suggested_alternative="Late fee",
            recommended_user_action="Remove",
            confidence=0.98
        ),
        ClauseAnalysisItem(
            clause_id="c_3",
            plain_english="Standard rent",
            risk_level=RiskLevel.GREEN,
            risk_reason="Fair",
            key_concern="None",
            suggested_alternative=None,
            recommended_user_action="Pay on time",
            confidence=0.95
        )
    ]
    missing = [
        MissingProtectionItem(
            name="Notice period",
            importance=ImportanceLevel.HIGH,
            reason="Missing",
            recommendation="Add 30-day notice"
        )
    ]
    res = calculate_fairness_score(items, missing, "rental")
    assert res.fairness_score < 70
    assert res.red_count == 2
    assert res.fairness_label in ["Needs Review", "High Risk"]
