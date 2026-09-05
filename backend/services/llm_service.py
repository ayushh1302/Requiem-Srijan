import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from backend.utils.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_MODEL,
    ANTHROPIC_MODEL,
    DEMO_MODE
)
from backend.models.schemas import (
    ClauseItem,
    ClauseAnalysisItem,
    ClauseSegmentationResult,
    RiskLevel,
    ImportanceLevel,
    MissingProtectionItem,
    MissingProtectionsResult,
    ChatResponse,
    SourceClause
)
from backend.services.mock_data_service import (
    get_prebuilt_analysis,
    generate_rule_based_clauses,
    generate_rule_based_analysis,
    get_grounded_mock_answer
)

class LLMService:
    def __init__(self):
        self.provider = LLM_PROVIDER.lower()
        self.demo_mode = DEMO_MODE or (not OPENAI_API_KEY and not ANTHROPIC_API_KEY)
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai_client(self):
        if self._openai_client is None and OPENAI_API_KEY:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
        return self._openai_client

    def _get_anthropic_client(self):
        if self._anthropic_client is None and ANTHROPIC_API_KEY:
            from anthropic import Anthropic
            self._anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        return self._anthropic_client

    def _clean_json_string(self, text: str) -> str:
        """Removes markdown code fences and whitespace from JSON response."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n", "", text)
            text = re.sub(r"\n```$", "", text)
        return text.strip()

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Calls the configured LLM provider and returns raw text."""
        if self.provider == "anthropic" and ANTHROPIC_API_KEY:
            client = self._get_anthropic_client()
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.2
            )
            return response.content[0].text
        else:
            client = self._get_openai_client()
            if not client:
                raise RuntimeError("No active OpenAI client configured.")
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content

    def segment_clauses(self, contract_text: str, filename: str = "") -> List[ClauseItem]:
        """
        Segments raw contract text into structured clauses.
        """
        if self.demo_mode or (not OPENAI_API_KEY and not ANTHROPIC_API_KEY):
            # Check for sample contract matches
            fn_lower = filename.lower()
            if "rental" in fn_lower or "rent" in fn_lower:
                return get_prebuilt_analysis("rental")["clauses"]
            elif "employment" in fn_lower or "job" in fn_lower or "offer" in fn_lower:
                return get_prebuilt_analysis("employment")["clauses"]
            elif "freelance" in fn_lower or "contractor" in fn_lower:
                return get_prebuilt_analysis("freelance")["clauses"]
            return generate_rule_based_clauses(contract_text)

        system_prompt = """You are ClauseClear's expert contract segmentation engine.
Your task is to split the uploaded legal document into distinct, meaningful clauses.

Rules:
1. Identify clause title/headline (e.g. "Termination", "Security Deposit", "Confidentiality").
2. Identify clause number if available (e.g. "1", "2.1", "Clause 4").
3. Assign a category: payment, termination, notice, confidentiality, liability, indemnity, dispute_resolution, deposit, intellectual_property, non_compete, working_hours, leave, renewal, rent, maintenance, penalties, obligations, miscellaneous.
4. Extract the exact verbatim original text for each clause without summarizing or modifying it.
5. If the document has no explicit clause numbers, group logical paragraphs into distinct clauses.

Return JSON format:
{
  "contract_type_hint": "rental|employment|freelance|service|generic",
  "clauses": [
    {
      "id": "clause_1",
      "number": "1",
      "title": "Termination",
      "category": "termination",
      "original_text": "..."
    }
  ]
}"""

        user_prompt = f"Contract Filename: {filename}\n\nFull Contract Text:\n{contract_text[:12000]}"

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            clean_json = self._clean_json_string(raw_response)
            data = json.loads(clean_json)
            clauses_data = data.get("clauses", [])

            clauses = []
            for idx, c in enumerate(clauses_data, start=1):
                clauses.append(
                    ClauseItem(
                        id=c.get("id", f"clause_{idx}"),
                        number=c.get("number", str(idx)),
                        title=c.get("title", f"Clause {idx}"),
                        category=c.get("category", "miscellaneous"),
                        original_text=c.get("original_text", "")
                    )
                )
            if clauses:
                return clauses
        except Exception as e:
            print(f"[LLMService] Clause segmentation failed: {e}. Falling back to rule-based segmenter.")

        return generate_rule_based_clauses(contract_text)

    def analyze_clauses(self, clauses: List[ClauseItem], contract_type: str = "generic") -> List[ClauseAnalysisItem]:
        """
        Analyzes each segmented clause for risk level, plain-English explanation, and negotiation suggestions.
        """
        if self.demo_mode or (not OPENAI_API_KEY and not ANTHROPIC_API_KEY):
            if contract_type in ["rental", "employment", "freelance"]:
                return get_prebuilt_analysis(contract_type)["analysis"]
            return generate_rule_based_analysis(clauses)

        system_prompt = f"""You are ClauseClear, an educational AI assistant that helps everyday non-lawyers understand contracts before signing.

Analyze every clause provided in the list.
For EACH clause, generate:
1. "plain_english": Simple 8th-grade explanation of what this clause means in practical life.
2. "risk_level": "GREEN" (standard/balanced/safe), "YELLOW" (caution/ambiguous/one-sided/needs attention), or "RED" (high risk/harmful/punitive/financially dangerous/severely one-sided).
3. "risk_reason": Clear explanation of why this risk level was assigned.
4. "key_concern": The biggest practical hazard for the signing party.
5. "suggested_alternative": For RED and YELLOW clauses, provide balanced, negotiation-ready alternative clause wording that protects the signer. For GREEN clauses, set to null.
6. "recommended_user_action": Concrete action the user should take (e.g. "Ask to insert 30-day notice", "Confirm meter readings").
7. "confidence": A float between 0.85 and 0.99.

Important:
- Do not invent laws or legal representation.
- Be objective and educational.

Return valid JSON:
{{
  "analysis": [
    {{
      "clause_id": "clause_1",
      "plain_english": "...",
      "risk_level": "GREEN|YELLOW|RED",
      "risk_reason": "...",
      "key_concern": "...",
      "suggested_alternative": "...",
      "recommended_user_action": "...",
      "confidence": 0.95
    }}
  ]
}}"""

        clauses_payload = [
            {"id": c.id, "title": c.title, "category": c.category, "original_text": c.original_text}
            for c in clauses
        ]

        user_prompt = f"Contract Type: {contract_type}\nClauses to analyze:\n{json.dumps(clauses_payload, indent=2)}"

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            clean_json = self._clean_json_string(raw_response)
            data = json.loads(clean_json)
            analysis_data = data.get("analysis", [])

            results = []
            for item in analysis_data:
                risk_str = item.get("risk_level", "GREEN").upper()
                if risk_str not in ["GREEN", "YELLOW", "RED"]:
                    risk_str = "YELLOW"

                results.append(
                    ClauseAnalysisItem(
                        clause_id=item.get("clause_id", ""),
                        plain_english=item.get("plain_english", ""),
                        risk_level=RiskLevel(risk_str),
                        risk_reason=item.get("risk_reason", ""),
                        key_concern=item.get("key_concern", ""),
                        suggested_alternative=item.get("suggested_alternative"),
                        recommended_user_action=item.get("recommended_user_action", "Review carefully."),
                        confidence=float(item.get("confidence", 0.92))
                    )
                )
            if results:
                return results
        except Exception as e:
            print(f"[LLMService] Clause analysis LLM failed: {e}. Using fallback rule-based analyzer.")

        return generate_rule_based_analysis(clauses)

    def answer_contract_question(
        self,
        question: str,
        retrieved_clauses: List[ClauseItem]
    ) -> ChatResponse:
        """
        Answers a user question strictly grounded on the retrieved clauses.
        """
        if self.demo_mode or (not OPENAI_API_KEY and not ANTHROPIC_API_KEY):
            return get_grounded_mock_answer(question, retrieved_clauses)

        system_prompt = """You are ClauseClear's contract-grounded legal assistant.

Rules:
1. Answer the user ONLY using the provided retrieved contract clauses.
2. NEVER use outside legal knowledge as if it appears in the contract.
3. If the retrieved clauses do NOT contain enough information to answer the question, explicitly say:
   "The uploaded contract does not clearly address this." and set "grounded": false.
4. Always cite the specific clause IDs and titles used in your answer.
5. Do not provide definitive legal advice or guarantee court outcomes.

Return JSON format:
{
  "answer": "...",
  "source_clauses": [
    {
      "clause_id": "clause_1",
      "title": "Termination",
      "snippet": "..."
    }
  ],
  "grounded": true
}"""

        context_text = "\n\n".join([
            f"[{c.id}] {c.title} ({c.category}):\n{c.original_text}"
            for c in retrieved_clauses
        ])

        user_prompt = f"User Question: {question}\n\nRetrieved Contract Clauses:\n{context_text}"

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            clean_json = self._clean_json_string(raw_response)
            data = json.loads(clean_json)

            sources = [
                SourceClause(
                    clause_id=s.get("clause_id", ""),
                    title=s.get("title", ""),
                    snippet=s.get("snippet", "")
                )
                for s in data.get("source_clauses", [])
            ]

            return ChatResponse(
                answer=data.get("answer", "The contract does not clearly address this."),
                source_clauses=sources,
                grounded=data.get("grounded", True),
                confidence_note="Grounded in retrieved contract clauses."
            )
        except Exception as e:
            print(f"[LLMService] Chat question failed: {e}. Falling back to mock grounded answer.")
            return get_grounded_mock_answer(question, retrieved_clauses)
