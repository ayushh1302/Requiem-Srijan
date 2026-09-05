import re
from typing import List, Dict, Any, Tuple
from backend.models.schemas import (
    ClauseItem,
    ClauseAnalysisItem,
    RiskLevel,
    ImportanceLevel,
    MissingProtectionItem,
    FairnessScoreResult,
    SourceClause,
    ChatResponse
)

# ==========================================
# PRE-BUILT HIGH-FIDELITY SAMPLE CONTRACT DATA
# ==========================================

MOCK_RENTAL_ANALYSIS = {
    "contract_type": "rental",
    "clauses": [
        ClauseItem(
            id="clause_1",
            number="1",
            title="Premises & Monthly Rent",
            category="rent",
            original_text="The Tenant agrees to pay a monthly rent of INR 35,000 payable in advance by the 5th day of every calendar month via bank transfer to the Landlord's designated bank account."
        ),
        ClauseItem(
            id="clause_2",
            number="2",
            title="Security Deposit & Forfeiture",
            category="deposit",
            original_text="The Tenant shall deposit INR 1,50,000 as refundable security deposit. In the event of any delay in rent payment exceeding 7 days, the Landlord reserves the absolute right to forfeit the entire security deposit without prior notice."
        ),
        ClauseItem(
            id="clause_3",
            number="3",
            title="Immediate Unilateral Eviction",
            category="termination",
            original_text="The Landlord may terminate this agreement and require the Tenant to vacate the premises within 24 hours at any time during the tenancy without assigning any reason or notice."
        ),
        ClauseItem(
            id="clause_4",
            number="4",
            title="Maintenance and Repairs",
            category="maintenance",
            original_text="The Tenant shall be entirely responsible for all repairs, whether major, structural, or minor, including roof leakage, electrical wiring, plumbing, and wall repainting at Tenant's sole expense."
        ),
        ClauseItem(
            id="clause_5",
            number="5",
            title="Landlord Inspection & Entry",
            category="obligations",
            original_text="The Landlord or their authorized agents shall have the right to enter and inspect the premises at any hour of the day or night without prior notice to the Tenant."
        ),
        ClauseItem(
            id="clause_6",
            number="6",
            title="Prohibition of Subletting",
            category="obligations",
            original_text="The Tenant shall not sublet, assign, or part with possession of the premises or any part thereof to any third party without express prior written consent of the Landlord."
        ),
        ClauseItem(
            id="clause_7",
            number="7",
            title="Utility & Electricity Charges",
            category="payment",
            original_text="The Tenant shall promptly pay all charges for electricity, water, and internet consumed on the premises directly to the respective authorities as per actual meter readings."
        ),
        ClauseItem(
            id="clause_8",
            number="8",
            title="Dispute Resolution and Jurisdiction",
            category="dispute_resolution",
            original_text="Any dispute or difference arising out of or in connection with this agreement shall be subject to the exclusive jurisdiction of the competent civil courts at Pune, Maharashtra."
        )
    ],
    "analysis": [
        ClauseAnalysisItem(
            clause_id="clause_1",
            plain_english="You must pay INR 35,000 rent each month by the 5th day directly to the landlord's bank account.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard payment terms with a clear due date and transparent payment method.",
            key_concern="Ensuring funds are transferred on time to avoid default penalties.",
            suggested_alternative=None,
            recommended_user_action="Set up a monthly standing instruction or bank transfer reminder for the 3rd of each month.",
            confidence=0.95
        ),
        ClauseAnalysisItem(
            clause_id="clause_2",
            plain_english="You pay a deposit of INR 1.5 Lakhs, but if your rent is more than 7 days late even once, the landlord claims they can keep all your deposit money forever.",
            risk_level=RiskLevel.RED,
            risk_reason="Highly punitive and one-sided. Forfeiting an entire deposit over a minor rent delay is excessive and unfair.",
            key_concern="You could lose INR 1,50,000 over a single banking holiday or minor delayed salary.",
            suggested_alternative="In the event of delayed rent exceeding 7 days, a reasonable late fee of INR 100 per day shall apply. The security deposit shall remain refundable upon lease conclusion minus verified unpaid dues.",
            recommended_user_action="Insist on replacing total forfeiture with a nominal daily late fee and a 15-day grace notice.",
            confidence=0.96
        ),
        ClauseAnalysisItem(
            clause_id="clause_3",
            plain_english="The landlord claims the power to throw you out of the apartment within 24 hours at any time, for no stated reason.",
            risk_level=RiskLevel.RED,
            risk_reason="Extreme risk. Eliminates tenant housing stability and violates standard mutual notice principles.",
            key_concern="You can be rendered homeless overnight with zero time to find alternative accommodation.",
            suggested_alternative="Either party may terminate this agreement by providing at least 30 days prior written notice, or immediately only in the case of a material, un-remedied breach after 14 days written notice.",
            recommended_user_action="Do not sign without changing this to a mandatory 30-day mutual written notice period.",
            confidence=0.98
        ),
        ClauseAnalysisItem(
            clause_id="clause_4",
            plain_english="You are forced to pay for all building repairs—even major structural issues like leaking roofs or damaged building wiring that landlords normally own.",
            risk_level=RiskLevel.RED,
            risk_reason="Shifts major landlord property ownership liabilities and building maintenance costs onto a temporary tenant.",
            key_concern="You could get stuck with tens of thousands of rupees in repair bills for pre-existing structural damage.",
            suggested_alternative="The Landlord shall be responsible for all structural, plumbing, and major repairs exceeding INR 1,000 not caused by Tenant negligence. Tenant shall handle minor routine maintenance.",
            recommended_user_action="Request clear demarcation: landlord pays structural/major repairs, tenant covers minor consumables under INR 1,000.",
            confidence=0.94
        ),
        ClauseAnalysisItem(
            clause_id="clause_5",
            plain_english="The landlord or their staff can walk into your rented home at any time, day or night, without telling you beforehand.",
            risk_level=RiskLevel.YELLOW,
            risk_reason="Severe privacy intrusion. Standard leases require advance written notice during reasonable daytime hours.",
            key_concern="Loss of privacy, personal security, and quiet enjoyment of your home.",
            suggested_alternative="The Landlord may inspect the premises upon providing at least 24 hours prior notice, during reasonable daytime hours (10:00 AM to 7:00 PM), in the presence of the Tenant.",
            recommended_user_action="Add a requirement for 24-hour prior notice during daytime hours only.",
            confidence=0.92
        ),
        ClauseAnalysisItem(
            clause_id="clause_6",
            plain_english="You cannot rent out rooms or pass the lease to someone else without the landlord's written permission.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard clause in residential leasing to prevent unauthorized occupants.",
            key_concern="Ensure you do not host long-term paying roommates without landlord consent.",
            suggested_alternative=None,
            recommended_user_action="Confirm that immediate family or visiting guests are permitted without formal approval.",
            confidence=0.96
        ),
        ClauseAnalysisItem(
            clause_id="clause_7",
            plain_english="You pay your own electricity, water, and internet bills based on your actual consumption.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard and balanced utility payment responsibility.",
            key_concern="Verify starting meter readings upon move-in day.",
            suggested_alternative=None,
            recommended_user_action="Take photos of utility meters and verify zero pending arrears on the day of taking possession.",
            confidence=0.97
        ),
        ClauseAnalysisItem(
            clause_id="clause_8",
            plain_english="Any legal disputes must be filed in civil courts located in Pune, Maharashtra.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard jurisdiction clause matching the location of the property.",
            key_concern="Confirm Pune is accessible to you if any legal issue arises.",
            suggested_alternative=None,
            recommended_user_action="Encourage adding an amicable 15-day mediation step before court filing.",
            confidence=0.93
        )
    ]
}

MOCK_EMPLOYMENT_ANALYSIS = {
    "contract_type": "employment",
    "clauses": [
        ClauseItem(
            id="clause_1",
            number="1",
            title="Designation and Monthly Remuneration",
            category="payment",
            original_text="The Employee is appointed as Software Engineer with an annual CTC of INR 8,50,000 payable monthly on the last working day of each calendar month after statutory tax deductions."
        ),
        ClauseItem(
            id="clause_2",
            number="2",
            title="Working Hours & Mandatory 24/7 Availability",
            category="working_hours",
            original_text="Standard working hours are 9:00 AM to 6:00 PM, Monday to Friday. However, the Employee agrees to remain on-call 24 hours a day, 7 days a week including weekends, with no overtime compensation."
        ),
        ClauseItem(
            id="clause_3",
            number="3",
            title="Comprehensive Post-Employment Non-Compete",
            category="non_compete",
            original_text="For a period of 36 months following termination of employment for any reason, the Employee shall not work for, consult, or start any business anywhere in India that operates in the technology sector."
        ),
        ClauseItem(
            id="clause_4",
            number="4",
            title="Intellectual Property & Personal Inventions",
            category="intellectual_property",
            original_text="All inventions, software, code, designs, or ideas conceived by the Employee at any time during their employment, whether on personal devices or outside work hours, shall become the sole property of the Company."
        ),
        ClauseItem(
            id="clause_5",
            number="5",
            title="Termination and Notice Period",
            category="termination",
            original_text="The Company may terminate the Employee with 3 days notice without cause. The Employee must provide at least 90 days notice before resigning, or forfeit 3 months gross salary."
        ),
        ClauseItem(
            id="clause_6",
            number="6",
            title="Confidentiality & Non-Disclosure",
            category="confidentiality",
            original_text="The Employee agrees to keep all proprietary client data, source code, trade secrets, and financial details strictly confidential both during and after the tenure of employment."
        ),
        ClauseItem(
            id="clause_7",
            number="7",
            title="Probation Period and Confirmation",
            category="obligations",
            original_text="The initial probation period shall be 6 months. The Company may extend probation at its sole discretion without specifying reasons."
        )
    ],
    "analysis": [
        ClauseAnalysisItem(
            clause_id="clause_1",
            plain_english="You will work as a Software Engineer for INR 8.5 Lakhs annual salary, paid monthly on the last working day.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard and clear compensation structure.",
            key_concern="Verify the exact fixed vs variable bonus breakdown in the annexed CTC annexure.",
            suggested_alternative=None,
            recommended_user_action="Request the detailed salary component breakdown (Basic, HRA, Special Allowance, PF).",
            confidence=0.96
        ),
        ClauseAnalysisItem(
            clause_id="clause_2",
            plain_english="While normal hours are 9 to 6, the company demands you be available 24/7 every day including weekends without any extra pay.",
            risk_level=RiskLevel.RED,
            risk_reason="Excessive and unhealthy demand that destroys work-life balance with zero compensation for overtime or on-call duty.",
            key_concern="Constant uncompensated burnout and unpredictable work schedules.",
            suggested_alternative="Employee will work standard 40-hour weeks. Any required emergency on-call duty outside hours will be rotated with advance notice and compensated with on-call allowances or compensatory off.",
            recommended_user_action="Negotiate clear on-call schedules, emergency limits, and compensatory time off.",
            confidence=0.95
        ),
        ClauseAnalysisItem(
            clause_id="clause_3",
            plain_english="You are prohibited from taking any tech job or starting any tech business anywhere in India for 3 years after leaving.",
            risk_level=RiskLevel.RED,
            risk_reason="Extremely oppressive and restrictive. Under Indian Contract Act (Section 27), post-employment non-competes restraining lawful profession are generally void and unenforceable.",
            key_concern="The company may use this threatening wording to block your future career transitions.",
            suggested_alternative="The non-compete clause shall apply strictly during active employment. Post-employment protections shall be limited to non-solicitation of company clients and staff for 12 months.",
            recommended_user_action="Request striking the 3-year post-employment restriction or replacing it with standard non-solicitation.",
            confidence=0.97
        ),
        ClauseAnalysisItem(
            clause_id="clause_4",
            plain_english="The company claims ownership of all personal coding projects and hobby apps you build on your own laptop on weekends.",
            risk_level=RiskLevel.YELLOW,
            risk_reason="Overbroad IP assignment that captures unrelated personal hobbies developed without company tools or company time.",
            key_concern="You could lose ownership of your personal open-source projects or side startups.",
            suggested_alternative="Company ownership applies solely to intellectual property created during working hours, using Company resources, or directly related to the Company's business lines.",
            recommended_user_action="Add an exclusion carving out pre-existing personal projects and unrelated weekend hobby code.",
            confidence=0.94
        ),
        ClauseAnalysisItem(
            clause_id="clause_5",
            plain_english="The company can fire you with only 3 days notice, but you are trapped for 90 days if you want to quit.",
            risk_level=RiskLevel.RED,
            risk_reason="Heavily asymmetric notice period that creates severe job insecurity while limiting your ability to take new job offers.",
            key_concern="Asymmetry: 3 days vs 90 days. Most new employers will not wait 90 days.",
            suggested_alternative="Either party may terminate employment by providing 30 days prior written notice or basic salary in lieu thereof.",
            recommended_user_action="Insist on a reciprocal 30-day or 60-day notice period for both employee and employer.",
            confidence=0.98
        ),
        ClauseAnalysisItem(
            clause_id="clause_6",
            plain_english="You must not disclose company code, client data, or secret business details to outsiders.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard and necessary confidentiality safeguard.",
            key_concern="Do not copy company source code or client databases to personal cloud storage.",
            suggested_alternative=None,
            recommended_user_action="Ensure confidentiality excludes publicly known information and standard general industry skills.",
            confidence=0.97
        ),
        ClauseAnalysisItem(
            clause_id="clause_7",
            plain_english="You have a 6-month probation period which the company can keep extending indefinitely.",
            risk_level=RiskLevel.YELLOW,
            risk_reason="Uncapped probation extensions delay benefits confirmation and notice parity.",
            key_concern="Being stuck in permanent probation without formal confirmation.",
            suggested_alternative="The probation period shall be 3 months, extendable at most once for an additional 3 months upon providing specific written performance feedback.",
            recommended_user_action="Request a maximum cap on probation extension and automatic confirmation upon completion.",
            confidence=0.91
        )
    ]
}

MOCK_FREELANCE_ANALYSIS = {
    "contract_type": "freelance",
    "clauses": [
        ClauseItem(
            id="clause_1",
            number="1",
            title="Scope of Work and Deliverables",
            category="obligations",
            original_text="The Contractor will design and build a responsive web application as specified in the agreed project roadmap."
        ),
        ClauseItem(
            id="clause_2",
            number="2",
            title="Unlimited Free Revisions",
            category="obligations",
            original_text="The Contractor agrees to provide unlimited revisions, redesigns, and additional feature modifications at no extra cost until the Client expresses 100% complete subjective satisfaction."
        ),
        ClauseItem(
            id="clause_3",
            number="3",
            title="Payment Schedule and Delay",
            category="payment",
            original_text="The total project fee is INR 1,20,000 payable upon full client sign-off. The Client reserves the right to withhold payment indefinitely if any milestone is delayed by more than 24 hours."
        ),
        ClauseItem(
            id="clause_4",
            number="4",
            title="Intellectual Property Assignment",
            category="intellectual_property",
            original_text="All intellectual property, source code, and design assets shall belong immediately to the Client upon creation, regardless of whether payments have been made."
        ),
        ClauseItem(
            id="clause_5",
            number="5",
            title="Late Delivery Penalty",
            category="penalties",
            original_text="For every day of delay in delivery beyond the target timeline, the Contractor shall pay a penalty of 5% of the total project value to the Client."
        ),
        ClauseItem(
            id="clause_6",
            number="6",
            title="Independent Contractor Status",
            category="miscellaneous",
            original_text="The Contractor is an independent contractor and not an employee. The Contractor is responsible for their own equipment, taxes, and insurance."
        )
    ],
    "analysis": [
        ClauseAnalysisItem(
            clause_id="clause_1",
            plain_english="You will build a responsive web application following the agreed roadmap.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard scope definition.",
            key_concern="Ensure the roadmap has clear, enumerated feature bullet points.",
            suggested_alternative=None,
            recommended_user_action="Attach a signed feature checklist as Annexure A to avoid scope creep.",
            confidence=0.94
        ),
        ClauseAnalysisItem(
            clause_id="clause_2",
            plain_english="The client expects you to do infinite free redesigns and add new features endlessly until they feel satisfied.",
            risk_level=RiskLevel.RED,
            risk_reason="Severe scope creep trap. 'Unlimited revisions' based on subjective satisfaction allows client exploitation.",
            key_concern="You could spend 6 months working on a 1-month project for zero additional pay.",
            suggested_alternative="The project fee includes up to two (2) rounds of revisions per milestone. Any subsequent revisions or scope changes shall be billed at INR 1,500/hour.",
            recommended_user_action="Cap revisions to 2 rounds and define an hourly rate for extra changes.",
            confidence=0.98
        ),
        ClauseAnalysisItem(
            clause_id="clause_3",
            plain_english="All your money is held until the very end, and if you are 1 day late, the client claims they can withhold payment forever.",
            risk_level=RiskLevel.RED,
            risk_reason="Extreme cash-flow risk. 100% payment on final delivery leaves the contractor vulnerable to non-payment.",
            key_concern="Total non-payment after delivering weeks of labor.",
            suggested_alternative="Payment shall be structured in milestones: 30% upfront deposit, 40% upon beta delivery, and 30% upon final launch. Invoices are due within 15 days.",
            recommended_user_action="Demand a 30%-40% upfront deposit before starting any coding.",
            confidence=0.97
        ),
        ClauseAnalysisItem(
            clause_id="clause_4",
            plain_english="The client owns your code the moment you type it, even if they never pay you a single rupee.",
            risk_level=RiskLevel.RED,
            risk_reason="Removes all freelancer leverage. IP should only transfer once full payment clears.",
            key_concern="The client can take your source code, ghost you, and deploy it without paying.",
            suggested_alternative="All intellectual property rights and code ownership shall transfer to Client solely upon receipt of 100% full and final payment.",
            recommended_user_action="Condition IP transfer strictly upon receipt of final cleared payment.",
            confidence=0.99
        ),
        ClauseAnalysisItem(
            clause_id="clause_5",
            plain_english="You are fined 5% of the entire project value for every single day a deadline slips.",
            risk_level=RiskLevel.RED,
            risk_reason="Disproportionate penalty. A 20-day delay wipes out 100% of your earnings, even if caused by client feedback delays.",
            key_concern="Losing all project earnings due to client communication bottlenecks.",
            suggested_alternative="Timelines shall adjust automatically for client feedback delays. Liquidated damages, if any, shall be capped at a maximum of 5% total project value.",
            recommended_user_action="Remove daily penalties or cap total delay penalties at 5% while pausing timers during client reviews.",
            confidence=0.96
        ),
        ClauseAnalysisItem(
            clause_id="clause_6",
            plain_english="You are an independent freelancer and manage your own taxes and laptop.",
            risk_level=RiskLevel.GREEN,
            risk_reason="Standard independent contractor status clause.",
            key_concern="Ensure you account for GST and income tax filings.",
            suggested_alternative=None,
            recommended_user_action="Ensure your invoice includes any applicable GST and tax details.",
            confidence=0.95
        )
    ]
}

def get_prebuilt_analysis(contract_type: str) -> Dict[str, Any]:
    if contract_type == "rental":
        return MOCK_RENTAL_ANALYSIS
    elif contract_type == "employment":
        return MOCK_EMPLOYMENT_ANALYSIS
    elif contract_type == "freelance":
        return MOCK_FREELANCE_ANALYSIS
    return MOCK_RENTAL_ANALYSIS

def generate_rule_based_clauses(text: str) -> List[ClauseItem]:
    """
    Intelligent regex-based segmenter for generic or custom contracts when in demo mode.
    Splits by numbers, headers, or double line-breaks.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    clauses = []

    clause_idx = 1
    for p in paragraphs:
        if len(p) < 25:
            continue

        # Check for heading pattern e.g. "1. Termination" or "Clause 3 - Payment"
        header_match = re.match(r"^((?:Clause|Section|Article|\d+)\s*[:.\-–]?\s*[\d\w\s]{2,30})[:.\-–\n]", p)
        if header_match:
            title = header_match.group(1).strip()
            title = re.sub(r"^[\d.\s\-–]+", "", title).strip() or f"Section {clause_idx}"
            number = str(clause_idx)
        else:
            first_line = p.split("\n")[0][:40]
            title = first_line if len(first_line) > 5 else f"Clause {clause_idx}"
            number = str(clause_idx)

        # Categorize
        p_lower = p.lower()
        category = "miscellaneous"
        if any(w in p_lower for w in ["rent", "lease", "tenant", "landlord"]):
            category = "rent"
        elif any(w in p_lower for w in ["pay", "salary", "fee", "compensation", "inr", "invoice"]):
            category = "payment"
        elif any(w in p_lower for w in ["terminate", "termination", "cancel", "vacate"]):
            category = "termination"
        elif any(w in p_lower for w in ["notice", "days notice"]):
            category = "notice"
        elif any(w in p_lower for w in ["deposit", "security deposit"]):
            category = "deposit"
        elif any(w in p_lower for w in ["non-compete", "restraint", "compete"]):
            category = "non_compete"
        elif any(w in p_lower for w in ["intellectual property", "copyright", "patent", "inventions"]):
            category = "intellectual_property"
        elif any(w in p_lower for w in ["confidential", "proprietary", "secret"]):
            category = "confidentiality"
        elif any(w in p_lower for w in ["liability", "indemnify", "indemnification", "damages"]):
            category = "liability"
        elif any(w in p_lower for w in ["dispute", "arbitration", "jurisdiction", "court"]):
            category = "dispute_resolution"
        elif any(w in p_lower for w in ["hours", "working hours", "overtime", "weekend"]):
            category = "working_hours"

        clauses.append(
            ClauseItem(
                id=f"clause_{clause_idx}",
                number=number,
                title=title[:45],
                category=category,
                original_text=p
            )
        )
        clause_idx += 1
        if clause_idx > 15:
            break

    return clauses

def generate_rule_based_analysis(clauses: List[ClauseItem]) -> List[ClauseAnalysisItem]:
    """
    Intelligent heuristic analysis for clauses in demo mode.
    """
    analysis_items = []

    for cl in clauses:
        text_lower = cl.original_text.lower()

        # Risk heuristics
        if any(w in text_lower for w in ["forfeit the entire", "without notice", "24 hours", "unlimited revisions", "sole property of company at any time", "36 months", "immediate termination without cause", "sole discretion without reason"]):
            risk_level = RiskLevel.RED
            risk_reason = "Contains potentially punitive, one-sided, or severely restrictive terms with minimal protection for the signer."
            key_concern = "High financial or operational risk; provides unilateral advantage to the drafting party."
            suggested_alternative = f"Either party may exercise rights under this clause only upon providing at least 30 days written notice and reasonable cure opportunity."
            recommended_action = "Do not accept this clause in its current form. Request mutual notice and a reasonable grace period."
        elif any(w in text_lower for w in ["at any hour", "delayed payment", "penalty", "broad non-disclosure", "discretion", "reimbursement", "extend probation"]):
            risk_level = RiskLevel.YELLOW
            risk_reason = "Contains ambiguous terms or one-sided conditions that warrant clarification before signing."
            key_concern = "Potential ambiguity that could lead to unexpected friction or costs."
            suggested_alternative = f"The terms of this {cl.title} shall be exercised reasonably during standard business hours with prior written notice."
            recommended_action = "Clarify the exact scope, notice requirements, and exceptions in writing."
        else:
            risk_level = RiskLevel.GREEN
            risk_reason = "Standard contractual clause with balanced mutual obligations."
            key_concern = "Ensure compliance with the stated timelines and obligations."
            suggested_alternative = None
            recommended_action = "Review to ensure alignment with your agreed expectations."

        # Plain English summary
        words = cl.original_text.split()
        summary = " ".join(words[:25]) + ("..." if len(words) > 25 else "")
        plain_english = f"This clause defines terms for {cl.title.lower()}. Specifically: {summary}"

        analysis_items.append(
            ClauseAnalysisItem(
                clause_id=cl.id,
                plain_english=plain_english,
                risk_level=risk_level,
                risk_reason=risk_reason,
                key_concern=key_concern,
                suggested_alternative=suggested_alternative,
                recommended_user_action=recommended_action,
                confidence=0.92
            )
        )

    return analysis_items

def get_grounded_mock_answer(question: str, clauses: List[ClauseItem]) -> ChatResponse:
    """
    Provides contract-grounded chatbot answers in DEMO_MODE.
    """
    q_lower = question.lower()

    # Search for matching clauses
    matched_clauses = []
    for cl in clauses:
        cl_text_lower = cl.original_text.lower()
        # Check relevance
        keywords = [w for w in q_lower.split() if len(w) > 3 and w not in ["what", "when", "where", "how", "does", "have", "with", "this", "that", "from", "about"]]
        match_count = sum(1 for kw in keywords if kw in cl_text_lower or kw in cl.title.lower())
        if match_count > 0:
            matched_clauses.append((cl, match_count))

    matched_clauses.sort(key=lambda x: x[1], reverse=True)

    if matched_clauses:
        best_clause, _ = matched_clauses[0]
        snippet = best_clause.original_text[:120] + "..." if len(best_clause.original_text) > 120 else best_clause.original_text
        source = SourceClause(clause_id=best_clause.id, title=best_clause.title, snippet=snippet)

        answer = f"Based on **{best_clause.title}** ({best_clause.id}), the contract states:\n\n> \"{best_clause.original_text}\"\n\nThis means that the document directly governs this matter under this provision."
        return ChatResponse(
            answer=answer,
            source_clauses=[source],
            grounded=True,
            confidence_note="Directly extracted from contract clause text."
        )
    else:
        return ChatResponse(
            answer="The uploaded contract does not clearly address this question. There are no clauses in the document that specify terms regarding this topic.",
            source_clauses=[],
            grounded=False,
            confidence_note="No matching clause found in the uploaded contract."
        )
