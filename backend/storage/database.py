import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from backend.utils.config import SQLITE_DB_PATH
from backend.models.schemas import (
    ClauseItem,
    ClauseAnalysisItem,
    FairnessScoreResult,
    MissingProtectionItem,
    ContractAnalysisResponse,
    SourceClause,
    RiskLevel
)

def get_db_connection() -> sqlite3.Connection:
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        contract_type TEXT,
        filename TEXT,
        file_type TEXT
    );

    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        page_count INTEGER DEFAULT 1,
        char_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS clauses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        clause_id TEXT NOT NULL,
        number TEXT,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'miscellaneous',
        original_text TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        clause_id TEXT NOT NULL,
        plain_english TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        risk_reason TEXT NOT NULL,
        key_concern TEXT NOT NULL,
        suggested_alternative TEXT,
        recommended_user_action TEXT NOT NULL,
        confidence REAL DEFAULT 0.9,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS fairness_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        fairness_score INTEGER NOT NULL,
        fairness_label TEXT NOT NULL,
        summary TEXT NOT NULL,
        green_count INTEGER DEFAULT 0,
        yellow_count INTEGER DEFAULT 0,
        red_count INTEGER DEFAULT 0,
        missing_count INTEGER DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS missing_protections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        name TEXT NOT NULL,
        importance TEXT NOT NULL,
        reason TEXT NOT NULL,
        recommendation TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        source_clauses TEXT,
        grounded INTEGER DEFAULT 1,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def save_session(session_id: str, filename: str, file_type: str, contract_type: str = "generic"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, filename, file_type, contract_type, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            filename=excluded.filename,
            file_type=excluded.file_type,
            contract_type=excluded.contract_type,
            last_active=CURRENT_TIMESTAMP
    """, (session_id, filename, file_type, contract_type))
    conn.commit()
    conn.close()

def save_raw_contract(session_id: str, filename: str, raw_text: str, page_count: int, char_count: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contracts WHERE session_id = ?", (session_id,))
    cursor.execute("""
        INSERT INTO contracts (session_id, filename, raw_text, page_count, char_count)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, filename, raw_text, page_count, char_count))
    conn.commit()
    conn.close()

def get_raw_contract(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def save_full_analysis(
    session_id: str,
    filename: str,
    file_type: str,
    contract_type: str,
    clauses: List[ClauseItem],
    analysis: List[ClauseAnalysisItem],
    fairness: FairnessScoreResult,
    missing_protections: List[MissingProtectionItem],
    page_count: int = 1,
    char_count: int = 0
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update session
    cursor.execute("""
        INSERT INTO sessions (session_id, filename, file_type, contract_type, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            filename=excluded.filename,
            file_type=excluded.file_type,
            contract_type=excluded.contract_type,
            last_active=CURRENT_TIMESTAMP
    """, (session_id, filename, file_type, contract_type))

    # Clear old records for this session
    cursor.execute("DELETE FROM clauses WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM analyses WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM fairness_scores WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM missing_protections WHERE session_id = ?", (session_id,))

    # Insert clauses
    for cl in clauses:
        cursor.execute("""
            INSERT INTO clauses (session_id, clause_id, number, title, category, original_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, cl.id, cl.number, cl.title, cl.category, cl.original_text))

    # Insert analysis
    for an in analysis:
        cursor.execute("""
            INSERT INTO analyses (session_id, clause_id, plain_english, risk_level, risk_reason, key_concern, suggested_alternative, recommended_user_action, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, an.clause_id, an.plain_english, an.risk_level.value, an.risk_reason, an.key_concern, an.suggested_alternative, an.recommended_user_action, an.confidence))

    # Insert fairness score
    cursor.execute("""
        INSERT INTO fairness_scores (session_id, fairness_score, fairness_label, summary, green_count, yellow_count, red_count, missing_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, fairness.fairness_score, fairness.fairness_label, fairness.summary, fairness.green_count, fairness.yellow_count, fairness.red_count, len(missing_protections)))

    # Insert missing protections
    for mp in missing_protections:
        cursor.execute("""
            INSERT INTO missing_protections (session_id, name, importance, reason, recommendation)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, mp.name, mp.importance.value, mp.reason, mp.recommendation))

    conn.commit()
    conn.close()

def get_full_analysis(session_id: str) -> Optional[ContractAnalysisResponse]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    session = cursor.fetchone()
    if not session:
        conn.close()
        return None

    cursor.execute("SELECT * FROM contracts WHERE session_id = ?", (session_id,))
    contract = cursor.fetchone()
    page_count = contract["page_count"] if contract else 1
    char_count = contract["char_count"] if contract else 0

    cursor.execute("SELECT * FROM clauses WHERE session_id = ?", (session_id,))
    clause_rows = cursor.fetchall()
    clauses = [
        ClauseItem(
            id=r["clause_id"],
            number=r["number"],
            title=r["title"],
            category=r["category"],
            original_text=r["original_text"]
        )
        for r in clause_rows
    ]

    cursor.execute("SELECT * FROM analyses WHERE session_id = ?", (session_id,))
    analysis_rows = cursor.fetchall()
    analysis = [
        ClauseAnalysisItem(
            clause_id=r["clause_id"],
            plain_english=r["plain_english"],
            risk_level=RiskLevel(r["risk_level"]),
            risk_reason=r["risk_reason"],
            key_concern=r["key_concern"],
            suggested_alternative=r["suggested_alternative"],
            recommended_user_action=r["recommended_user_action"],
            confidence=r["confidence"]
        )
        for r in analysis_rows
    ]

    cursor.execute("SELECT * FROM fairness_scores WHERE session_id = ?", (session_id,))
    score_row = cursor.fetchone()
    if score_row:
        fairness = FairnessScoreResult(
            fairness_score=score_row["fairness_score"],
            fairness_label=score_row["fairness_label"],
            summary=score_row["summary"],
            green_count=score_row["green_count"],
            yellow_count=score_row["yellow_count"],
            red_count=score_row["red_count"],
            missing_count=score_row["missing_count"]
        )
    else:
        fairness = FairnessScoreResult(
            fairness_score=50,
            fairness_label="Needs Review",
            summary="Analysis in progress",
            green_count=0,
            yellow_count=0,
            red_count=0
        )

    cursor.execute("SELECT * FROM missing_protections WHERE session_id = ?", (session_id,))
    mp_rows = cursor.fetchall()
    missing_protections = [
        MissingProtectionItem(
            name=r["name"],
            importance=r["importance"],
            reason=r["reason"],
            recommendation=r["recommendation"]
        )
        for r in mp_rows
    ]

    conn.close()

    return ContractAnalysisResponse(
        session_id=session["session_id"],
        filename=session["filename"] or "document",
        file_type=session["file_type"] or "pdf",
        contract_type=session["contract_type"] or "generic",
        page_count=page_count,
        char_count=char_count,
        fairness=fairness,
        clauses=clauses,
        analysis=analysis,
        missing_protections=missing_protections,
        executive_summary=fairness.summary,
        created_at=session["created_at"]
    )

def save_chat_message(session_id: str, role: str, content: str, source_clauses: List[Dict[str, Any]] = None, grounded: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor()
    sources_json = json.dumps(source_clauses) if source_clauses else "[]"
    cursor.execute("""
        INSERT INTO chat_messages (session_id, role, content, source_clauses, grounded)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, content, sources_json, 1 if grounded else 0))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "role": r["role"],
            "content": r["content"],
            "source_clauses": json.loads(r["source_clauses"]) if r["source_clauses"] else [],
            "grounded": bool(r["grounded"]),
            "timestamp": r["timestamp"]
        })
    return result

def clear_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM contracts WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM clauses WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM analyses WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM fairness_scores WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM missing_protections WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# Initialize DB on module load
init_db()
