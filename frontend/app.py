import streamlit as st
import requests
import json
import time
from pathlib import Path

# ==========================================
# STREAMLIT PAGE CONFIG & THEME
# ==========================================
st.set_page_config(
    page_title="ClauseClear — Understand Before You Sign",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000"
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = BASE_DIR / "sample_contracts"

# ==========================================
# CUSTOM CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero header */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        color: #F8FAFC;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60A5FA, #38BDF8, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-tagline {
        font-size: 1.15rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 6px;
    }
    .hero-subtext {
        font-size: 0.92rem;
        color: #94A3B8;
        line-height: 1.5;
    }
    .hackathon-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #93C5FD;
        border: 1px solid rgba(59, 130, 246, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 10px;
    }

    /* Disclaimer box */
    .disclaimer-banner {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 0.85rem;
        color: #92400E;
        line-height: 1.4;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
        transition: transform 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Clause Cards */
    .clause-card-red {
        background: #FEF2F2;
        border-left: 5px solid #EF4444;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border-top: 1px solid #FEE2E2;
        border-right: 1px solid #FEE2E2;
        border-bottom: 1px solid #FEE2E2;
    }
    .clause-card-yellow {
        background: #FFFBEB;
        border-left: 5px solid #F59E0B;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border-top: 1px solid #FEF3C7;
        border-right: 1px solid #FEF3C7;
        border-bottom: 1px solid #FEF3C7;
    }
    .clause-card-green {
        background: #F0FDF4;
        border-left: 5px solid #10B981;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border-top: 1px solid #DCFCE7;
        border-right: 1px solid #DCFCE7;
        border-bottom: 1px solid #DCFCE7;
    }

    .badge-red {
        background-color: #DC2626;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-yellow {
        background-color: #D97706;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-green {
        background-color: #16A34A;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .negotiation-box {
        background: #F0FDF4;
        border: 1px dashed #16A34A;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 10px;
        font-size: 0.88rem;
        color: #14532D;
    }

    .key-concern-box {
        background: #FEF2F2;
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.85rem;
        color: #991B1B;
        font-weight: 500;
    }

    /* Chat message styling */
    .citation-tag {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "session_id" not in st.session_state:
    st.session_state.session_id = f"demo_{int(time.time())}"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def reset_all():
    sess_id = st.session_state.session_id
    try:
        requests.post(f"{BACKEND_URL}/reset/{sess_id}", timeout=5)
    except Exception:
        pass
    st.session_state.session_id = f"demo_{int(time.time())}"
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.uploaded_file_name = None
    st.rerun()

def analyze_document_bytes(file_bytes: bytes, filename: str):
    with st.spinner(f"⚡ Parsing and reading {filename}..."):
        try:
            files = {"file": (filename, file_bytes)}
            data = {"session_id": st.session_state.session_id}
            upload_resp = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=30)
            if upload_resp.status_code != 200:
                st.error(f"Upload failed: {upload_resp.json().get('detail', 'Unknown error')}")
                return
        except Exception as e:
            st.error(f"Could not connect to backend at {BACKEND_URL}. Ensure backend is running. Error: {e}")
            return

    with st.spinner("🤖 AI is segmenting clauses, evaluating risk levels & fairness score..."):
        try:
            analyze_payload = {"session_id": st.session_state.session_id}
            resp = requests.post(f"{BACKEND_URL}/analyze", json=analyze_payload, timeout=60)
            if resp.status_code == 200:
                st.session_state.analysis_result = resp.json()
                st.session_state.uploaded_file_name = filename
                st.success(f"Analysis complete for '{filename}'!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(f"Analysis failed: {resp.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### ⚖️ **ClauseClear Controls**")
    st.caption("AI Contract Analyzer & Negotiation Assistant")

    # Sample Contract Quick-Load
    st.markdown("---")
    st.markdown("#### ⚡ **Quick Test Samples**")
    st.caption("Test ClauseClear instantly without uploading files:")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🏠 Rental Lease", use_container_width=True):
            sample_path = SAMPLE_DIR / "rental_agreement_sample.txt"
            if sample_path.exists():
                with open(sample_path, "rb") as f:
                    analyze_document_bytes(f.read(), "Pune_Rental_Agreement_Sample.txt")
    with col_s2:
        if st.button("💼 Job Offer", use_container_width=True):
            sample_path = SAMPLE_DIR / "employment_offer_sample.txt"
            if sample_path.exists():
                with open(sample_path, "rb") as f:
                    analyze_document_bytes(f.read(), "Software_Engineer_Offer_Letter.txt")

    if st.button("💻 Freelance Contract", use_container_width=True):
        sample_path = SAMPLE_DIR / "freelance_agreement_sample.txt"
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                analyze_document_bytes(f.read(), "Freelance_Dev_Contract.txt")

    st.markdown("---")
    st.markdown("#### ⚙️ **Session Info**")
    st.code(f"Session: {st.session_state.session_id[:16]}...", language="text")

    if st.button("🔄 Reset & Clear Analysis", use_container_width=True, type="secondary"):
        reset_all()

    st.markdown("---")
    st.markdown("""
    **Srijan Hackathon**  
    *GH Raisoni College of Engineering & Management, Pune*  
    *Computer Society of India*  
    """)

# ==========================================
# HERO HEADER & BRANDING
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">
        <span>⚖️ CLAUSECLEAR</span>
    </div>
    <div class="hero-tagline">Understand before you sign.</div>
    <div class="hero-subtext">
        A patient, knowledgeable friend who reads complex legal contracts, explains them in plain English, flags unfair clauses, uncovers missing protections, and gives you negotiation-ready wording.
    </div>
    <div class="hackathon-badge">🏆 Srijan Hackathon • CSI GHRCEM Pune</div>
</div>
""", unsafe_allow_html=True)

# Educational Disclaimer Banner
st.markdown("""
<div class="disclaimer-banner">
    ⚠️ <b>Legal Disclaimer:</b> ClauseClear provides AI-generated educational information and is <b>not</b> a substitute for qualified legal counsel. For high-stakes legal, commercial, or tenancy matters, consult a licensed advocate.
</div>
""", unsafe_allow_html=True)

# ==========================================
# FILE UPLOAD & OVERVIEW SECTION
# ==========================================
if not st.session_state.analysis_result:
    st.markdown("### 📤 **1. Upload Your Contract**")
    st.write("Upload any PDF, DOCX, or Text contract. ClauseClear processes documents in memory for this session.")

    uploaded_file = st.file_uploader(
        "Choose a contract file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        help="Max file size 15MB. Supported formats: .pdf, .docx, .txt"
    )

    if uploaded_file is not None:
        if st.button("🚀 Analyze Contract Now", type="primary", use_container_width=True):
            file_bytes = uploaded_file.getvalue()
            analyze_document_bytes(file_bytes, uploaded_file.name)

    st.markdown("---")
    st.info("💡 **Judges / Evaluators:** You can also click any of the **Quick Test Samples** in the left sidebar to analyze pre-loaded rental, employment, or freelance contracts in 1 click!")

# ==========================================
# MAIN ANALYSIS INTERFACE (WHEN ANALYZED)
# ==========================================
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    fairness = res.get("fairness", {})
    clauses = res.get("clauses", [])
    analysis = res.get("analysis", [])
    missing_prot = res.get("missing_protections", [])

    # Map analysis by clause_id for fast lookup
    analysis_map = {a["clause_id"]: a for a in analysis}

    # Executive Metric Cards
    score = fairness.get("fairness_score", 50)
    score_label = fairness.get("fairness_label", "Needs Review")
    score_color = "#16A34A" if score >= 85 else ("#CA8A04" if score >= 70 else ("#EA580C" if score >= 50 else "#DC2626"))

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {score_color};">
            <div class="metric-value" style="color: {score_color};">{score}/100</div>
            <div class="metric-label">Fairness: {score_label}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #16A34A;">
            <div class="metric-value" style="color: #16A34A;">{fairness.get("green_count", 0)}</div>
            <div class="metric-label">Safe (Green)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #D97706;">
            <div class="metric-value" style="color: #D97706;">{fairness.get("yellow_count", 0)}</div>
            <div class="metric-label">Caution (Yellow)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #DC2626;">
            <div class="metric-value" style="color: #DC2626;">{fairness.get("red_count", 0)}</div>
            <div class="metric-label">High Risk (Red)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m5:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #3B82F6;">
            <div class="metric-value" style="color: #3B82F6;">{len(missing_prot)}</div>
            <div class="metric-label">Missing Protections</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Tabs for Navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard & Overview",
        "🔍 Clause Analysis",
        "🛡️ Missing Protections",
        "✉️ Negotiation Email",
        "💬 Ask ClauseClear (RAG)",
        "📄 Download Report",
        "ℹ️ About & Roadmap"
    ])

    # ----------------------------------------------------
    # TAB 1: DASHBOARD & OVERVIEW
    # ----------------------------------------------------
    with tab1:
        st.markdown("### 📋 **Executive Summary**")
        st.info(f"**Document:** `{res.get('filename')}` | **Contract Type:** `{res.get('contract_type', '').title()}` | **Total Clauses:** `{len(clauses)}`")

        st.markdown(f"**AI Assessment:** {res.get('executive_summary')}")

        st.markdown("---")
        st.markdown("#### 🎯 **Fairness Score Breakdown**")
        st.caption("How ClauseClear calculated the 0-100 Fairness Score:")

        breakdown_notes = fairness.get("breakdown_notes", [])
        if breakdown_notes:
            for note in breakdown_notes:
                st.write(f"• {note}")
        else:
            st.write("• Calculated based on clause risk distribution and missing protection safeguards.")

        # Key High Risk Alerts
        red_items = [c for c in clauses if analysis_map.get(c["id"], {}).get("risk_level") == "RED"]
        if red_items:
            st.markdown("---")
            st.markdown(f"#### 🚨 **Top {len(red_items)} High-Risk Watch-Outs**")
            for cl in red_items:
                an = analysis_map.get(cl["id"], {})
                st.error(f"**{cl.get('title')}**: {an.get('key_concern')} — *{an.get('recommended_user_action')}*")

    # ----------------------------------------------------
    # TAB 2: CLAUSE-BY-CLAUSE ANALYSIS
    # ----------------------------------------------------
    with tab2:
        st.markdown("### 🔍 **Clause-by-Clause Plain-English Breakdown**")
        st.caption("Review each clause, understand what it means in plain English, and get negotiation-ready alternative wording.")

        # Filter and Search row
        filter_col1, filter_col2 = st.columns([1, 2])
        with filter_col1:
            risk_filter = st.selectbox(
                "Filter by Risk Level:",
                ["All Clauses", "🔴 Red (High Risk)", "🟡 Yellow (Caution)", "🟢 Green (Safe)"]
            )
        with filter_col2:
            search_kw = st.text_input("🔎 Search clauses by keyword:", placeholder="e.g., eviction, deposit, non-compete, hours, penalty...")

        # Filter clauses
        filtered_clauses = []
        for c in clauses:
            an = analysis_map.get(c["id"], {})
            lvl = an.get("risk_level", "GREEN")

            # Check risk filter
            matches_risk = True
            if "Red" in risk_filter and lvl != "RED":
                matches_risk = False
            elif "Yellow" in risk_filter and lvl != "YELLOW":
                matches_risk = False
            elif "Green" in risk_filter and lvl != "GREEN":
                matches_risk = False

            # Check search keyword
            matches_search = True
            if search_kw.strip():
                kw = search_kw.strip().lower()
                combined = (c.get("title", "") + " " + c.get("original_text", "") + " " + an.get("plain_english", "")).lower()
                if kw not in combined:
                    matches_search = False

            if matches_risk and matches_search:
                filtered_clauses.append((c, an))

        st.write(f"Showing **{len(filtered_clauses)}** of **{len(clauses)}** clauses:")

        for cl, an in filtered_clauses:
            risk_lvl = an.get("risk_level", "GREEN")
            card_class = "clause-card-red" if risk_lvl == "RED" else ("clause-card-yellow" if risk_lvl == "YELLOW" else "clause-card-green")
            badge_class = "badge-red" if risk_lvl == "RED" else ("badge-yellow" if risk_lvl == "YELLOW" else "badge-green")
            badge_text = "HIGH RISK" if risk_lvl == "RED" else ("CAUTION" if risk_lvl == "YELLOW" else "SAFE & STANDARD")

            # Indian legal callouts
            legal_tag = ""
            title_lower = cl.get("title", "").lower()
            text_lower = cl.get("original_text", "").lower()
            if "non-compete" in title_lower or "non-compete" in text_lower or "36 months" in text_lower:
                legal_tag = " • 🇮🇳 <span style='color: #DC2626; font-weight: 600;'>Section 27 Indian Contract Act Alert</span>"
            elif "eviction" in title_lower or "24 hours" in text_lower:
                legal_tag = " • 🇮🇳 <span style='color: #DC2626; font-weight: 600;'>Model Tenancy Act / Rent Control Warning</span>"
            elif "forfeit" in title_lower or "forfeit" in text_lower:
                legal_tag = " • 🇮🇳 <span style='color: #D97706; font-weight: 600;'>Excessive Penalty Alert</span>"

            with st.expander(f"[{badge_text}] {cl.get('title')} ({cl.get('category', 'general').title()})", expanded=(risk_lvl == "RED")):
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #0F172A;">{cl.get('title')}{legal_tag}</h4>
                        <span class="{badge_class}">{badge_text}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <b>🗣️ Plain-English Translation:</b><br/>
                        <span style="color: #1E293B;">{an.get('plain_english')}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <b>⚠️ Risk Reason:</b> {an.get('risk_reason')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if an.get("key_concern"):
                    st.markdown(f"""
                    <div class="key-concern-box">
                        <b>🎯 Key Concern:</b> {an.get('key_concern')}
                    </div>
                    """, unsafe_allow_html=True)

                # Negotiation Alternative
                if an.get("suggested_alternative"):
                    st.markdown(f"""
                    <div class="negotiation-box">
                        <b>✍️ Negotiation-Ready Alternative Wording:</b><br/>
                        <i>"{an.get('suggested_alternative')}"</i>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(an.get('suggested_alternative'), language="text")

                st.markdown(f"**Recommended Action:** `{an.get('recommended_user_action')}`")

                with st.expander("📜 View Verbatim Original Text"):
                    st.code(cl.get("original_text"), language="text")

    # ----------------------------------------------------
    # TAB 3: MISSING PROTECTIONS DETECTOR
    # ----------------------------------------------------
    with tab3:
        st.markdown("### 🛡️ **Missing Protections & Safeguards**")
        st.caption(f"Comparison against standard checklist for **{res.get('contract_type', '').title()}** contracts.")

        if not missing_prot:
            st.success("✅ Great news! This contract covers all standard protections checked by ClauseClear.")
        else:
            for mp in missing_prot:
                imp = mp.get("importance", "MEDIUM")
                imp_color = "#DC2626" if imp == "HIGH" else ("#D97706" if imp == "MEDIUM" else "#2563EB")

                st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; border-left: 4px solid {imp_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #0F172A;">{mp.get('name')}</h4>
                        <span style="background: {imp_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">{imp} IMPORTANCE</span>
                    </div>
                    <p style="margin: 8px 0 4px 0; color: #334155; font-size: 0.9rem;">
                        <b>Why this is missing & why it matters:</b> {mp.get('reason')}
                    </p>
                    <p style="margin: 0; color: #15803D; font-size: 0.88rem;">
                        <b>💡 Suggested Clause to Add:</b> <i>"{mp.get('recommendation')}"</i>
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 4: NEGOTIATION EMAIL GENERATOR
    # ----------------------------------------------------
    with tab4:
        st.markdown("### ✉️ **Pre-Drafted Negotiation Email**")
        st.caption("A courteous, professional email draft ready to send to the landlord, employer, or client requesting fair revisions:")

        # Generate Email Text
        risky_clauses_for_email = [
            (c, analysis_map.get(c["id"], {}))
            for c in clauses
            if analysis_map.get(c["id"], {}).get("risk_level") in ["RED", "YELLOW"]
            and analysis_map.get(c["id"], {}).get("suggested_alternative")
        ]

        recipient_title = "Landlord" if res.get("contract_type") == "rental" else ("Hiring Team" if res.get("contract_type") == "employment" else "Client")
        doc_label = "Lease Agreement" if res.get("contract_type") == "rental" else ("Offer Letter & Employment Agreement" if res.get("contract_type") == "employment" else "Services Agreement")

        email_lines = [
            f"Subject: Review & Proposed Minor Clarifications — {res.get('filename', doc_label)}",
            "",
            f"Dear {recipient_title},",
            "",
            f"Thank you for sharing the draft {doc_label}. I have carefully reviewed the terms and am eager to proceed. To ensure mutual clarity and a smooth relationship, I would appreciate your consideration of a few balanced adjustments to the wording:",
            ""
        ]

        for idx, (c, an) in enumerate(risky_clauses_for_email, start=1):
            email_lines.append(f"{idx}. Regarding {c.get('title')} ({c.get('id')}):")
            email_lines.append(f"   • Current Wording: \"{c.get('original_text')[:100]}...\"")
            email_lines.append(f"   • Proposed Alternative: \"{an.get('suggested_alternative')}\"")
            email_lines.append(f"   • Rationale: To ensure standard mutual notice and fair protection for both parties.")
            email_lines.append("")

        if missing_prot:
            high_missing = [m for m in missing_prot if m.get("importance") == "HIGH"]
            if high_missing:
                email_lines.append("Additionally, could we please insert explicit standard terms for:")
                for hm in high_missing[:2]:
                    email_lines.append(f"   • {hm.get('name')}: \"{hm.get('recommendation')}\"")
                email_lines.append("")

        email_lines.append("Please let me know if these adjustments work for you. Looking forward to your response and finalizing the agreement.")
        email_lines.append("")
        email_lines.append("Warm regards,")
        email_lines.append("[Your Name]")
        email_lines.append("[Your Phone Number]")

        full_email_text = "\n".join(email_lines)

        st.text_area("📋 Copyable Email Draft:", value=full_email_text, height=350)
        st.info("💡 **Tip:** You can copy the text above and paste it directly into your email client!")

    # ----------------------------------------------------
    # TAB 5: ASK CLAUSECLEAR (GROUNDED RAG CHATBOT)
    # ----------------------------------------------------
    with tab5:
        st.markdown("### 💬 **Ask ClauseClear — Grounded Contract Assistant**")
        st.caption("Ask questions about your uploaded agreement. Answers are **strictly grounded** on the contract clauses.")

        # Quick question chips
        st.markdown("##### 💡 Suggested Questions:")
        chip_col1, chip_col2, chip_col3 = st.columns(3)

        user_query = None
        with chip_col1:
            if st.button("What is the notice period for termination?"):
                user_query = "What is the notice period for termination?"
        with chip_col2:
            if st.button("Can my deposit be forfeited or deducted?"):
                user_query = "Can my deposit be forfeited or deducted?"
        with chip_col3:
            if st.button("Are there any non-compete or repair penalties?"):
                user_query = "Are there any non-compete or repair penalties?"

        # Chat display
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.write(msg["content"])
                    if msg.get("source_clauses"):
                        st.markdown("**Citations & Sources:**")
                        for src in msg["source_clauses"]:
                            st.markdown(f"<span class='citation-tag'>📌 {src.get('title')} ({src.get('clause_id')})</span>", unsafe_allow_html=True)

        # Chat Input
        input_prompt = st.chat_input("Ask a question about this contract...")
        if input_prompt:
            user_query = input_prompt

        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant", avatar="⚖️"):
                with st.spinner("Searching contract clauses with vector retrieval..."):
                    try:
                        chat_resp = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={"session_id": st.session_state.session_id, "message": user_query},
                            timeout=30
                        )
                        if chat_resp.status_code == 200:
                            ans_data = chat_resp.json()
                            ans_text = ans_data.get("answer", "")
                            sources = ans_data.get("source_clauses", [])

                            st.write(ans_text)
                            if sources:
                                st.markdown("**Citations & Sources:**")
                                for src in sources:
                                    st.markdown(f"<span class='citation-tag'>📌 {src.get('title')} ({src.get('clause_id')})</span>", unsafe_allow_html=True)

                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": ans_text,
                                "source_clauses": sources
                            })
                        else:
                            st.error(f"Chat error: {chat_resp.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to chat API: {e}")

    # ----------------------------------------------------
    # TAB 6: DOWNLOAD REPORT
    # ----------------------------------------------------
    with tab6:
        st.markdown("### 📄 **Download Executive Summary Report**")
        st.write("Generate a downloadable PDF executive brief containing your Fairness Score, Red/Yellow flagged clauses, missing protections, and negotiation-ready alternative wording.")

        try:
            report_url = f"{BACKEND_URL}/report/{st.session_state.session_id}"
            report_resp = requests.get(report_url, timeout=30)
            if report_resp.status_code == 200:
                st.download_button(
                    label="📥 Download PDF Analysis Report",
                    data=report_resp.content,
                    file_name=f"ClauseClear_Analysis_{st.session_state.session_id[:8]}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                st.success("✅ PDF report generated and ready for instant download!")
            else:
                st.error("Report could not be generated at this time.")
        except Exception as e:
            st.warning(f"Backend report generator notice: {e}")

    # ----------------------------------------------------
    # TAB 7: ABOUT & ROADMAP
    # ----------------------------------------------------
    with tab7:
        st.markdown("### ℹ️ **About ClauseClear & Srijan Hackathon**")
        st.markdown("""
        **ClauseClear** was created for the **Srijan Hackathon** hosted by **GH Raisoni College of Engineering and Management, Pune** & the **Computer Society of India (CSI)**.

        #### 🎯 **The Problem**
        Millions of renters, fresh graduates, freelancers, and small business owners sign contracts every day without understanding the fine print. Traditional legal consultation is expensive, slow, and inaccessible to everyday citizens.

        #### 💡 **The ClauseClear Solution**
        ClauseClear bridges this justice gap by providing:
        1. **Plain-English Explanations** at an 8th-grade reading level.
        2. **Risk Flagging** with intuitive Green / Yellow / Red badges.
        3. **Negotiation-Ready Alternative Wording** so users can push back constructively.
        4. **Transparent Fairness Score (0-100)** to summarize contract balance.
        5. **Missing Protections Detector** comparing against standard safeguards.
        6. **Contract-Grounded RAG Assistant** with ChromaDB vector embeddings.

        ---
        #### 🇮🇳 **Indian Legal Tech Roadmap (Future Scope)**
        - 🌐 **Multilingual Support:** Hindi (हिंदी), Marathi (मराठी), and regional Indian language translations.
        - 📱 **Mobile & WhatsApp Bot:** Quick photo analysis via WhatsApp.
        - ⚖️ **Indian Law Alignment:** Automatic checks against *Model Tenancy Act 2021*, *Indian Contract Act Section 27*, and *New Labour Codes*.
        - 🔍 **Scanned OCR:** Tesseract / Document AI for non-searchable stamp-paper contracts.
        - 🤝 **Pro-Bono Legal Aid Directory:** 1-click escalation to certified local legal clinics in Pune and Maharashtra.
        """)
