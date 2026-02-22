"""Neon Postgres database client for ScamGotchi."""

import os
import json
from typing import Optional
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras


class NeonDB:
    """Client for Neon Postgres database."""

    def __init__(self):
        self.database_url = os.getenv("NEON_DATABASE_URL", "")
        self._conn = None
        self._available = False

    def _get_connection(self):
        """Get or create a database connection."""
        if self._conn is None or self._conn.closed:
            try:
                self._conn = psycopg2.connect(self.database_url)
                self._conn.autocommit = True
                self._available = True
            except Exception as e:
                print(f"[neon_db] Connection failed: {e}")
                self._available = False
                self._conn = None
                raise
        return self._conn

    def init_tables(self):
        """Create tables if they don't exist."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    pet_state JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id SERIAL PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0,
                    street_smarts INTEGER NOT NULL DEFAULT 0,
                    scams_blocked INTEGER NOT NULL DEFAULT 0,
                    savings_protected FLOAT NOT NULL DEFAULT 0,
                    personality TEXT DEFAULT 'chill',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS scam_log (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    scam_type TEXT,
                    is_scam BOOLEAN,
                    player_said_scam BOOLEAN,
                    reasoning_score INTEGER DEFAULT 0,
                    outcome TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS uncai_stats (
                    user_id TEXT PRIMARY KEY,
                    stats JSONB DEFAULT '{}',
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS uncai_attempts (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    item_id TEXT,
                    scam_type TEXT,
                    actual_is_scam BOOLEAN,
                    player_answer TEXT,
                    correct BOOLEAN,
                    reasoning_score INTEGER DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.close()
            self._available = True
            print("[neon_db] Tables initialized successfully")

        except Exception as e:
            print(f"[neon_db] Failed to initialize tables: {e}")
            self._available = False

    def get_leaderboard(self, limit: int = 20) -> list[dict]:
        """Get the top scores from the leaderboard."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                SELECT user_name, score, street_smarts, scams_blocked,
                       savings_protected, personality, created_at
                FROM leaderboard
                ORDER BY score DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            cur.close()
            # Convert to plain dicts with serializable values
            results = []
            for row in rows:
                d = dict(row)
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                results.append(d)
            return results
        except Exception as e:
            print(f"[neon_db] get_leaderboard failed: {e}")
            return []

    def submit_score(
        self,
        user_name: str,
        score: int,
        street_smarts: int,
        scams_blocked: int,
        savings_protected: float,
        personality: str,
    ) -> Optional[dict]:
        """Submit a score to the leaderboard."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO leaderboard (user_name, score, street_smarts, scams_blocked, savings_protected, personality)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_name, score, created_at
                """,
                (user_name, score, street_smarts, scams_blocked, savings_protected, personality),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] submit_score failed: {e}")
            return None

    def log_scam(
        self,
        user_id: str,
        scam_type: str,
        is_scam: bool,
        player_said_scam: bool,
        reasoning_score: int,
        outcome: str,
    ) -> Optional[dict]:
        """Log a scam interaction to the database."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO scam_log (user_id, scam_type, is_scam, player_said_scam, reasoning_score, outcome)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
                """,
                (user_id, scam_type, is_scam, player_said_scam, reasoning_score, outcome),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] log_scam failed: {e}")
            return None

    def get_uncai_stats(self, user_id: str) -> Optional[dict]:
        """Get UncAI stats for a user."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT user_id, stats, updated_at FROM uncai_stats WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                if d.get("updated_at"):
                    d["updated_at"] = d["updated_at"].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] get_uncai_stats failed: {e}")
            return None

    def save_uncai_stats(self, user_id: str, stats_json: dict) -> Optional[dict]:
        """Upsert UncAI stats for a user."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO uncai_stats (user_id, stats, updated_at)
                VALUES (%s, %s::jsonb, NOW())
                ON CONFLICT (user_id) DO UPDATE
                SET stats = EXCLUDED.stats,
                    updated_at = NOW()
                RETURNING user_id, stats, updated_at
                """,
                (user_id, json.dumps(stats_json)),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                if d.get("updated_at"):
                    d["updated_at"] = d["updated_at"].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] save_uncai_stats failed: {e}")
            return None

    def log_uncai_attempt(
        self,
        user_id: str,
        item_id: str,
        scam_type: Optional[str],
        actual_is_scam: bool,
        player_answer: str,
        correct: bool,
        reasoning_score: int,
    ) -> Optional[dict]:
        """Log an UncAI practice attempt."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO uncai_attempts
                    (user_id, item_id, scam_type, actual_is_scam, player_answer, correct, reasoning_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
                """,
                (
                    user_id,
                    item_id,
                    scam_type,
                    actual_is_scam,
                    player_answer,
                    correct,
                    reasoning_score,
                ),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] log_uncai_attempt failed: {e}")
            return None

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get a user by their ID."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT user_id, name, pet_state, created_at, updated_at FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                for key in ("created_at", "updated_at"):
                    if d.get(key):
                        d[key] = d[key].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] get_user failed: {e}")
            return None

    def save_user(self, user_id: str, name: str, pet_state_json: str) -> Optional[dict]:
        """Save or update a user with their pet state."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO users (user_id, name, pet_state, updated_at)
                VALUES (%s, %s, %s::jsonb, NOW())
                ON CONFLICT (user_id) DO UPDATE
                SET name = EXCLUDED.name,
                    pet_state = EXCLUDED.pet_state,
                    updated_at = NOW()
                RETURNING user_id, name, created_at, updated_at
                """,
                (user_id, name, pet_state_json),
            )
            row = cur.fetchone()
            cur.close()
            if row:
                d = dict(row)
                for key in ("created_at", "updated_at"):
                    if d.get(key):
                        d[key] = d[key].isoformat()
                return d
            return None
        except Exception as e:
            print(f"[neon_db] save_user failed: {e}")
            return None

    @property
    def is_available(self) -> bool:
        return self._available

    def close(self):
        """Close the database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
