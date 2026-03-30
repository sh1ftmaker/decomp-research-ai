"""SQLite state tracking for function decompilation progress."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Valid states in the state machine
STATES = [
    "UNSELECTED", "DECOMPILING", "BUILDING", "CLASSIFYING",
    "MATCHED", "COMPILE_ERROR", "SIZE_MISMATCH", "REGALLOC_ONLY",
    "AI_LOGIC_FIX", "AI_REGALLOC_FIX", "AI_SYNTAX_FIX",
    "PERMUTER", "SKIPPED", "FAILED",
]

TERMINAL_STATES = {"MATCHED", "SKIPPED", "FAILED"}


@dataclass
class FunctionState:
    func_name: str
    unit_name: str
    source_path: str
    asm_path: str
    size_bytes: int
    initial_match_pct: Optional[float]
    current_match_pct: Optional[float]
    state: str
    attempt_count: int
    logic_fix_attempts: int
    regalloc_fix_attempts: int
    permuter_best_score: Optional[int]
    last_error: Optional[str]


@dataclass
class Attempt:
    func_name: str
    state: str
    match_pct: Optional[float]
    diff_summary: Optional[str]
    ai_model: Optional[str]
    ai_prompt_tokens: Optional[int]
    ai_response_tokens: Optional[int]
    duration_secs: Optional[float]


class StateDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS functions (
                func_name TEXT PRIMARY KEY,
                unit_name TEXT NOT NULL,
                source_path TEXT NOT NULL,
                asm_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                initial_match_pct REAL,
                current_match_pct REAL,
                state TEXT NOT NULL DEFAULT 'UNSELECTED',
                attempt_count INTEGER DEFAULT 0,
                logic_fix_attempts INTEGER DEFAULT 0,
                regalloc_fix_attempts INTEGER DEFAULT 0,
                permuter_best_score INTEGER,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                func_name TEXT NOT NULL REFERENCES functions(func_name),
                state TEXT NOT NULL,
                match_pct REAL,
                diff_summary TEXT,
                ai_model TEXT,
                ai_prompt_tokens INTEGER,
                ai_response_tokens INTEGER,
                duration_secs REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_functions_state ON functions(state);
            CREATE INDEX IF NOT EXISTS idx_functions_unit ON functions(unit_name);
            CREATE INDEX IF NOT EXISTS idx_attempts_func ON attempts(func_name);
        """)
        self.conn.commit()

    def upsert_function(self, func_name: str, unit_name: str, source_path: str,
                        asm_path: str, size_bytes: int,
                        initial_match_pct: Optional[float] = None):
        self.conn.execute("""
            INSERT INTO functions (func_name, unit_name, source_path, asm_path,
                                   size_bytes, initial_match_pct, current_match_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(func_name) DO UPDATE SET
                initial_match_pct = COALESCE(excluded.initial_match_pct, initial_match_pct),
                size_bytes = excluded.size_bytes,
                updated_at = CURRENT_TIMESTAMP
        """, (func_name, unit_name, source_path, asm_path, size_bytes,
              initial_match_pct, initial_match_pct))
        self.conn.commit()

    def get_state(self, func_name: str) -> Optional[FunctionState]:
        row = self.conn.execute(
            "SELECT * FROM functions WHERE func_name = ?", (func_name,)
        ).fetchone()
        if not row:
            return None
        return FunctionState(
            func_name=row["func_name"], unit_name=row["unit_name"],
            source_path=row["source_path"], asm_path=row["asm_path"],
            size_bytes=row["size_bytes"],
            initial_match_pct=row["initial_match_pct"],
            current_match_pct=row["current_match_pct"],
            state=row["state"], attempt_count=row["attempt_count"],
            logic_fix_attempts=row["logic_fix_attempts"],
            regalloc_fix_attempts=row["regalloc_fix_attempts"],
            permuter_best_score=row["permuter_best_score"],
            last_error=row["last_error"],
        )

    def update_state(self, func_name: str, state: str, **kwargs):
        sets = ["state = ?", "updated_at = CURRENT_TIMESTAMP"]
        vals = [state]
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            vals.append(v)
        vals.append(func_name)
        self.conn.execute(
            f"UPDATE functions SET {', '.join(sets)} WHERE func_name = ?", vals
        )
        self.conn.commit()

    def increment(self, func_name: str, field: str):
        self.conn.execute(
            f"UPDATE functions SET {field} = {field} + 1, updated_at = CURRENT_TIMESTAMP "
            f"WHERE func_name = ?", (func_name,)
        )
        self.conn.commit()

    def log_attempt(self, attempt: Attempt):
        self.conn.execute("""
            INSERT INTO attempts (func_name, state, match_pct, diff_summary,
                                  ai_model, ai_prompt_tokens, ai_response_tokens,
                                  duration_secs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (attempt.func_name, attempt.state, attempt.match_pct,
              attempt.diff_summary, attempt.ai_model, attempt.ai_prompt_tokens,
              attempt.ai_response_tokens, attempt.duration_secs))
        self.conn.commit()

    def get_pending(self, batch_size: int = 10, exclude_units: set = None):
        """Get functions ready for processing, avoiding locked units."""
        exclude_units = exclude_units or set()
        placeholders = ",".join("?" * len(exclude_units)) if exclude_units else "''"
        rows = self.conn.execute(f"""
            SELECT * FROM functions
            WHERE state NOT IN ('MATCHED', 'SKIPPED', 'FAILED')
            AND unit_name NOT IN ({placeholders})
            ORDER BY
                CASE WHEN current_match_pct IS NOT NULL
                     THEN (100.0 - current_match_pct) ELSE 999 END ASC,
                size_bytes ASC
            LIMIT ?
        """, (*exclude_units, batch_size)).fetchall()
        return [FunctionState(
            func_name=r["func_name"], unit_name=r["unit_name"],
            source_path=r["source_path"], asm_path=r["asm_path"],
            size_bytes=r["size_bytes"], initial_match_pct=r["initial_match_pct"],
            current_match_pct=r["current_match_pct"], state=r["state"],
            attempt_count=r["attempt_count"],
            logic_fix_attempts=r["logic_fix_attempts"],
            regalloc_fix_attempts=r["regalloc_fix_attempts"],
            permuter_best_score=r["permuter_best_score"],
            last_error=r["last_error"],
        ) for r in rows]

    def get_total_tokens(self, func_name: str) -> int:
        row = self.conn.execute("""
            SELECT COALESCE(SUM(COALESCE(ai_prompt_tokens, 0) +
                                COALESCE(ai_response_tokens, 0)), 0) as total
            FROM attempts WHERE func_name = ?
        """, (func_name,)).fetchone()
        return row["total"]

    def get_stats(self) -> dict:
        stats = {}
        for state in STATES:
            row = self.conn.execute(
                "SELECT COUNT(*) as c FROM functions WHERE state = ?", (state,)
            ).fetchone()
            stats[state] = row["c"]
        return stats

    def close(self):
        self.conn.close()
