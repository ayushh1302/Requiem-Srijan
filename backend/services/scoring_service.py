import math
from typing import List, Dict, Any, Tuple
from backend.models.schemas import (
    RiskLevel,
    ImportanceLevel,
    ClauseAnalysisItem,
    MissingProtectionItem,
    FairnessScoreResult,
    MissingProtectionsResult
)

# Predefined standard checklists for contract types
STANDARD_PROTECTIONS_CATALOG = {
    "rental": [
        {
            "name": "Deposit Refund Timeline",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["deposit", "refund", "return", "security deposit", "30 days", "deduction"],
            "reason": "The contract should explicitly specify the exact timeframe (e.g. within 15-30 days) and conditions under which the security deposit will be returned.",
            "recommendation": "The Landlord shall inspect the premises and return the full security deposit, minus legitimate damages, within 30 days of lease termination."
        },
        {
            "name": "Mutual Notice Period for Termination",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["notice", "terminate", "eviction", "30 days notice", "written notice"],
            "reason": "Both tenant and landlord should have equal written notice requirements (e.g. 30-60 days) before termination without cause.",
            "recommendation": "Either party may terminate this agreement by providing at least 30 days prior written notice to the other party."
        },
        {
            "name": "Maintenance & Repair Responsibilities",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["maintenance", "repair", "structural", "major repair", "minor repair", "plumbing"],
            "reason": "Fair contracts clearly divide major structural repairs (landlord duty) vs minor routine wear-and-tear (tenant duty).",
            "recommendation": "The Landlord is responsible for structural repairs and electrical/plumbing installations, while the Tenant covers minor day-to-day repairs up to a specified threshold."
        },
        {
            "name": "Rent Escalation Limits",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["rent increase", "escalation", "increase", "percentage", "renewal rate"],
            "reason": "Uncapped rent hikes can force sudden displacement; standard agreements cap annual increases (typically 5%–10%).",
            "recommendation": "Any annual rent increase upon renewal shall not exceed 10% and requires at least 45 days advance written notice."
        },
        {
            "name": "Landlord Inspection Notice",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["inspection", "entry", "access", "visit", "24 hours", "prior notice"],
            "reason": "Protects tenant privacy by requiring the landlord to provide advance notice (e.g. 24-48 hours) before entering.",
            "recommendation": "The Landlord must provide at least 24 hours written notice before entering the premises for inspections or repairs during reasonable daytime hours."
        },
        {
            "name": "Utility & Maintenance Charge Breakdown",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["utility", "electricity", "water", "society charges", "maintenance fee"],
            "reason": "Clearly states which utilities (water, electricity, society maintenance) are included or billed separately.",
            "recommendation": "Tenant shall pay monthly electricity and water consumption directly, while society maintenance charges shall be borne by the Landlord."
        },
        {
            "name": "Dispute Resolution & Jurisdiction",
            "importance": ImportanceLevel.LOW,
            "keywords": ["dispute", "arbitration", "jurisdiction", "court", "mediation"],
            "reason": "Identifies the local city jurisdiction and mediation procedure if a disagreement arises.",
            "recommendation": "Any dispute arising under this agreement shall be settled through amicable discussion, or subject to the exclusive jurisdiction of local courts."
        }
    ],
    "employment": [
        {
            "name": "Clear Salary & Compensation Breakdown",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["salary", "compensation", "ctc", "payment date", "reimbursement", "bonus"],
            "reason": "The agreement must define base pay, pay cycle (e.g., by 5th of each month), deductions, and bonus terms.",
            "recommendation": "Salary will be credited monthly on or before the 1st working day, with a transparent salary slip detailing all statutory and tax deductions."
        },
        {
            "name": "Balanced Notice Period & Severance",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["notice period", "severance", "termination notice", "in lieu of notice", "resignation"],
            "reason": "Notice periods should be equal between employee and employer, preventing sudden layoffs without pay.",
            "recommendation": "Either party may terminate employment with 30 days written notice or base pay in lieu thereof."
        },
        {
            "name": "Standard Working Hours & Overtime Policy",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["working hours", "hours per week", "overtime", "weekend", "work schedule", "shifts"],
            "reason": "Uncapped working hours without overtime compensation lead to burnout and exploitation.",
            "recommendation": "Standard working hours shall be 40 hours per week (Monday through Friday). Any authorized overtime work will be compensated appropriately."
        },
        {
            "name": "Paid Leave & Holiday Entitlement",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["leave", "vacation", "sick leave", "casual leave", "paid time off", "pto", "public holidays"],
            "reason": "Contracts should explicitly outline earned leave, sick leave, maternity/paternity leave, and public holidays.",
            "recommendation": "Employee is entitled to at least 18 days of paid annual leave plus statutory sick leave and official public holidays."
        },
        {
            "name": "Reasonable Intellectual Property Assignment",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["intellectual property", "inventions", "copyright", "patent", "prior inventions", "personal time"],
            "reason": "IP assignment should only cover work created for the company during working hours, not personal side-projects on personal devices.",
            "recommendation": "Company owns intellectual property developed solely in the scope of employment using company resources, excluding prior inventions and unrelated personal projects."
        },
        {
            "name": "Reasonable & Enforceable Non-Compete Scope",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["non-compete", "restraint of trade", "geographic scope", "competing business"],
            "reason": "Overly broad post-employment non-compete clauses are restrictive and often unenforceable under Indian Section 27.",
            "recommendation": "Non-compete clauses should be restricted strictly during active employment or narrowly limited in geographic and business scope."
        },
        {
            "name": "Probation Period Terms & Confirmation",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["probation", "confirmation", "probationary period", "assessment", "3 months", "6 months"],
            "reason": "Specifies the exact length of probation (e.g. 3-6 months) and the criteria for formal confirmation.",
            "recommendation": "The probation period shall be 3 months, after which the employee is formally confirmed unless written feedback is provided."
        },
        {
            "name": "Workplace Safety & Harassment Policy (POSH)",
            "importance": ImportanceLevel.LOW,
            "keywords": ["harassment", "posh", "safety", "grievance", "internal committee"],
            "reason": "Guarantees formal internal grievance handling and compliance with statutory workplace safety norms.",
            "recommendation": "Employer maintains a zero-tolerance policy against harassment with an active Internal Complaints Committee (ICC)."
        }
    ],
    "freelance": [
        {
            "name": "Defined Project Scope & Deliverables",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["scope of work", "deliverables", "specifications", "sow", "requirements"],
            "reason": "Prevents 'scope creep' where the client demands additional unpaid tasks outside the original agreement.",
            "recommendation": "The Contractor will deliver strictly the milestones listed in Schedule A. Any additional feature requests will be quoted as separate work orders."
        },
        {
            "name": "Payment Milestone Schedule & Late Fee Clause",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["payment schedule", "milestone", "invoice", "late fee", "interest", "net 15", "net 30"],
            "reason": "Protects freelancers from unpaid invoices and delayed client processing.",
            "recommendation": "Invoices are payable within 15 days of issue. Invoices overdue past 30 days accrue a 1.5% monthly late interest charge."
        },
        {
            "name": "Revision Limits & Acceptance Period",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["revisions", "acceptance", "review period", "rounds of revisions", "sign-off"],
            "reason": "Without revision limits, clients can demand endless adjustments without additional pay.",
            "recommendation": "Each deliverable includes up to 2 rounds of client revisions. Deliverables not rejected in writing within 7 business days are deemed accepted."
        },
        {
            "name": "IP Transfer Conditioned Upon Full Payment",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["ip transfer", "ownership transfer", "upon full payment", "copyright assignment"],
            "reason": "Freelancers should retain ownership of work product until final payment has cleared.",
            "recommendation": "All copyright and intellectual property rights transfer to the Client solely upon receipt of 100% full and final payment."
        },
        {
            "name": "Kill Fee / Early Termination Compensation",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["kill fee", "early termination", "cancellation", "work completed to date"],
            "reason": "Guarantees compensation for hours and work completed if the client cancels the project prematurely.",
            "recommendation": "If Client terminates the project prior to completion, Freelancer shall be paid for all hours worked and milestones completed to date plus a 15% cancellation fee."
        },
        {
            "name": "Portfolio & Case Study Showcase Rights",
            "importance": ImportanceLevel.LOW,
            "keywords": ["portfolio", "showcase", "case study", "credit", "marketing"],
            "reason": "Allows the freelancer to showcase non-confidential parts of the project in their portfolio.",
            "recommendation": "Freelancer retains the right to display the completed work in online portfolios and case studies after public launch."
        }
    ],
    "generic": [
        {
            "name": "Clear Scope & Obligations",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["scope", "obligations", "responsibilities", "deliverables", "services"],
            "reason": "Both parties must have unequivocal clarity on exact deliverables and standards.",
            "recommendation": "Each party's responsibilities, standards, and performance timelines shall be explicitly itemized."
        },
        {
            "name": "Mutual Termination & Notice Period",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["termination", "notice", "written notice", "cure period", "default"],
            "reason": "Contracts should allow orderly exit and provide cure periods for minor breaches.",
            "recommendation": "Either party may terminate for convenience with 30 days written notice, or for cause after a 15-day breach cure window."
        },
        {
            "name": "Limitation of Liability Cap",
            "importance": ImportanceLevel.HIGH,
            "keywords": ["limitation of liability", "cap", "indirect damages", "consequential", "total fees"],
            "reason": "Prevents unlimited financial exposure from unforeseen contract disputes.",
            "recommendation": "Total aggregate liability of either party shall not exceed the total fees paid or payable under this agreement in the preceding 6 months."
        },
        {
            "name": "Mutual Confidentiality Safeguards",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["confidentiality", "proprietary", "non-disclosure", "confidential information"],
            "reason": "Protects proprietary business and personal data exchanged during the engagement.",
            "recommendation": "Both parties agree to protect and keep confidential all non-public proprietary materials for a period of 2 years."
        },
        {
            "name": "Dispute Resolution & Governing Law",
            "importance": ImportanceLevel.MEDIUM,
            "keywords": ["dispute resolution", "governing law", "arbitration", "jurisdiction"],
            "reason": "Clarifies the legal venue and mediation process to avoid costly court battles.",
            "recommendation": "Disputes shall be submitted to arbitration in accordance with local arbitration rules, under the governing laws of the local jurisdiction."
        }
    ]
}

def detect_contract_type(text: str, filename: str = "") -> str:
    """
    Infers the contract type from text and filename.
    """
    text_lower = (text + " " + filename).lower()

    # Keyword scoring
    rental_keywords = ["rent", "tenant", "landlord", "lease", "premises", "security deposit", "flat", "apartment", "house", "licensor", "licensee"]
    employment_keywords = ["employee", "employer", "employment", "salary", "probation", "ctc", "designation", "job offer", "annual leave", "working hours"]
    freelance_keywords = ["freelancer", "contractor", "client", "statement of work", "deliverables", "hourly rate", "milestone", "independent contractor", "project scope"]

    rental_score = sum(1 for kw in rental_keywords if kw in text_lower)
    employment_score = sum(1 for kw in employment_keywords if kw in text_lower)
    freelance_score = sum(1 for kw in freelance_keywords if kw in text_lower)

    if rental_score >= employment_score and rental_score >= freelance_score and rental_score >= 3:
        return "rental"
    elif employment_score >= rental_score and employment_score >= freelance_score and employment_score >= 3:
        return "employment"
    elif freelance_score >= 3:
        return "freelance"

    return "generic"

def evaluate_missing_protections(contract_type: str, full_text: str) -> List[MissingProtectionItem]:
    """
    Checks the contract against standard protections checklist for the identified type.
    """
    catalog = STANDARD_PROTECTIONS_CATALOG.get(contract_type, STANDARD_PROTECTIONS_CATALOG["generic"])
    text_lower = full_text.lower()

    missing: List[MissingProtectionItem] = []

    for item in catalog:
        # Check if any keyword matches
        found = False
        for kw in item["keywords"]:
            if kw.lower() in text_lower:
                found = True
                break

        if not found:
            missing.append(
                MissingProtectionItem(
                    name=item["name"],
                    importance=item["importance"],
                    reason=item["reason"],
                    recommendation=item["recommendation"]
                )
            )

    return missing

def calculate_fairness_score(
    analysis_items: List[ClauseAnalysisItem],
    missing_protections: List[MissingProtectionItem],
    contract_type: str = "generic"
) -> FairnessScoreResult:
    """
    Calculates a transparent, weighted fairness score (0 to 100).

    Scoring Model:
    - Base score: 100 points
    - GREEN clauses: +0 deductions (balanced/safe)
    - YELLOW clauses: -6 points each (moderate risk / ambiguity)
    - RED clauses: -16 points each (severe risk / one-sided punitive terms)
    - High Importance Missing Protections: -5 points each
    - Medium Importance Missing Protections: -3 points each
    - Low Importance Missing Protections: -1 point each
    - Ratio Penalty: If RED + YELLOW clauses exceed 40% of all clauses, apply a heavy imbalance deduction.
    """
    total_clauses = len(analysis_items)
    if total_clauses == 0:
        return FairnessScoreResult(
            fairness_score=50,
            fairness_label="Needs Review",
            summary="No clauses were detected for evaluation.",
            green_count=0,
            yellow_count=0,
            red_count=0,
            missing_count=len(missing_protections),
            breakdown_notes=["No clauses detected in document."]
        )

    green_count = sum(1 for c in analysis_items if c.risk_level == RiskLevel.GREEN)
    yellow_count = sum(1 for c in analysis_items if c.risk_level == RiskLevel.YELLOW)
    red_count = sum(1 for c in analysis_items if c.risk_level == RiskLevel.RED)

    # Base points
    score = 100.0
    breakdown_notes = []

    # Clause deductions
    yellow_deduction = yellow_count * 6.0
    red_deduction = red_count * 16.0

    score -= (yellow_deduction + red_deduction)
    if yellow_count > 0:
        breakdown_notes.append(f"-{int(yellow_deduction)} pts: {yellow_count} caution/ambiguous (Yellow) clauses")
    if red_count > 0:
        breakdown_notes.append(f"-{int(red_deduction)} pts: {red_count} high-risk/one-sided (Red) clauses")

    # Missing protections deduction
    high_missing = sum(1 for m in missing_protections if m.importance == ImportanceLevel.HIGH)
    med_missing = sum(1 for m in missing_protections if m.importance == ImportanceLevel.MEDIUM)
    low_missing = sum(1 for m in missing_protections if m.importance == ImportanceLevel.LOW)

    missing_deduction = (high_missing * 5.0) + (med_missing * 3.0) + (low_missing * 1.0)
    score -= missing_deduction

    if missing_deduction > 0:
        breakdown_notes.append(f"-{int(missing_deduction)} pts: {len(missing_protections)} missing standard safeguards")

    # Contract imbalance ratio penalty
    risky_ratio = (red_count + (yellow_count * 0.5)) / total_clauses
    if risky_ratio > 0.40:
        imbalance_penalty = min(20.0, (risky_ratio - 0.40) * 35.0)
        score -= imbalance_penalty
        breakdown_notes.append(f"-{int(imbalance_penalty)} pts: Structural contract imbalance ({int(risky_ratio*100)}% risky clauses)")

    # Bound score between 5 and 100
    final_score = int(max(5, min(100, round(score))))

    # Determine Label
    if final_score >= 85:
        fairness_label = "Fair"
    elif final_score >= 70:
        fairness_label = "Mostly Fair"
    elif final_score >= 50:
        fairness_label = "Needs Review"
    else:
        fairness_label = "High Risk"

    # Executive Summary generation
    if red_count == 0 and yellow_count <= 2 and high_missing == 0:
        summary = f"This {contract_type} agreement is well-balanced with mostly standard, safe terms. Overall protections are adequate."
    elif red_count >= 2 or final_score < 50:
        summary = f"This {contract_type} agreement contains {red_count} critical high-risk clauses and {len(missing_protections)} missing safeguards. Immediate renegotiation or clarification is strongly advised before signing."
    elif red_count == 1 or yellow_count >= 3:
        summary = f"Most terms are standard, but {red_count} high-risk clause and {yellow_count} ambiguous clauses warrant careful review and negotiation."
    else:
        summary = f"This contract is moderately fair ({fairness_label}), but contains {yellow_count} clauses and {len(missing_protections)} missing protections worth clarifying."

    return FairnessScoreResult(
        fairness_score=final_score,
        fairness_label=fairness_label,
        summary=summary,
        green_count=green_count,
        yellow_count=yellow_count,
        red_count=red_count,
        missing_count=len(missing_protections),
        breakdown_notes=breakdown_notes
    )
