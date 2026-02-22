"""UncAI practice engine for scam identification training."""

import json
import os
import random
import uuid
from typing import Optional

from models import ScamMessage, MessageSource, Personality
from reasoning_eval import evaluate_reasoning


class UncAIEngine:
    """Serve practice items and track performance in memory."""

    def __init__(self, data_dir: Optional[str] = None, db=None):
        base_dir = os.path.dirname(__file__)
        self.data_dir = data_dir or os.path.join(base_dir, "..", "data")
        self.seed_path = os.path.join(self.data_dir, "seed_scams.json")
        self.taxonomy_path = os.path.join(self.data_dir, "scam_taxonomy.json")
        self.seed_items: list[dict] = []
        self.taxonomy: dict[str, dict] = {}
        self._index: dict[str, dict] = {}
        self._stats: dict[str, dict] = {}
        self.db = db
        self.load_data()

    def load_data(self) -> None:
        """Load seed scams and taxonomy from disk."""
        self.seed_items = self._load_json_list(self.seed_path)
        taxonomy_list = self._load_json_list(self.taxonomy_path)
        self.taxonomy = {item.get("id"): item for item in taxonomy_list if item.get("id")}
        self._index = {}
        for item in self.seed_items:
            item_id = item.get("id") or f"seed_{uuid.uuid4()}"
            item["id"] = item_id
            self._index[item_id] = item

    @staticmethod
    def _load_json_list(path: str) -> list[dict]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return []

    def get_practice_item(
        self,
        scam_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Optional[dict]:
        """Return a practice item with scam details removed."""
        candidates = self.seed_items
        if scam_type:
            candidates = [item for item in candidates if item.get("scam_type") == scam_type]
        if source:
            candidates = [item for item in candidates if item.get("source") == source]
        if not candidates:
            return None

        item = random.choice(candidates)
        return self._public_item(item)

    def _public_item(self, item: dict) -> dict:
        """Hide scam indicators from practice item."""
        return {
            "id": item.get("id"),
            "source": item.get("source"),
            "sender": item.get("sender"),
            "subject": item.get("subject"),
            "content": item.get("content"),
        }

    async def evaluate_answer(
        self,
        item_id: str,
        answer: str,
        explanation: str,
        user_id: str = "default",
    ) -> Optional[dict]:
        """Evaluate a user's answer and update performance stats."""
        item = self._index.get(item_id)
        if not item:
            return None

        normalized = answer.strip().lower()
        player_says_scam = normalized == "scam"
        actual_is_scam = bool(item.get("is_scam"))
        correct = (player_says_scam and actual_is_scam) or (
            not player_says_scam and not actual_is_scam
        )

        reasoning_score = None
        reasoning_feedback = None
        red_flags_mentioned: list[str] = []
        if explanation and actual_is_scam and player_says_scam:
            try:
                source = MessageSource(item.get("source", "digital"))
            except ValueError:
                source = MessageSource.DIGITAL
            message = ScamMessage(
                id=item.get("id", ""),
                source=source,
                sender=item.get("sender", ""),
                subject=item.get("subject", ""),
                content=item.get("content", ""),
                scam_type=item.get("scam_type"),
                is_scam=actual_is_scam,
                tactics=item.get("tactics", []),
                severity=int(item.get("severity", 5)),
                red_flags=item.get("red_flags", []),
            )
            result = await evaluate_reasoning(
                message=message,
                explanation=explanation,
                personality=Personality.AGENT,
            )
            reasoning_score = result.score
            reasoning_feedback = result.feedback
            red_flags_mentioned = result.red_flags_mentioned

        feedback = self._build_feedback(
            actual_is_scam=actual_is_scam,
            correct=correct,
            item=item,
        )

        stats = self._update_stats(
            user_id=user_id,
            correct=correct,
            scam_type=item.get("scam_type"),
            reasoning_score=reasoning_score,
        )

        if self.db and self.db.is_available:
            self.db.save_uncai_stats(user_id, stats)
            self.db.log_uncai_attempt(
                user_id=user_id,
                item_id=item.get("id", ""),
                scam_type=item.get("scam_type"),
                actual_is_scam=actual_is_scam,
                player_answer=normalized,
                correct=correct,
                reasoning_score=reasoning_score or 0,
            )

        return {
            "correct": correct,
            "actual_is_scam": actual_is_scam,
            "scam_type": item.get("scam_type"),
            "feedback": feedback,
            "reveal": {
                "id": item.get("id"),
                "source": item.get("source"),
                "sender": item.get("sender"),
                "subject": item.get("subject"),
                "content": item.get("content"),
                "scam_type": item.get("scam_type"),
                "is_scam": actual_is_scam,
                "tactics": item.get("tactics", []),
                "severity": item.get("severity", 0),
                "red_flags": item.get("red_flags", []),
            },
            "reasoning": {
                "score": reasoning_score,
                "feedback": reasoning_feedback,
                "red_flags_mentioned": red_flags_mentioned,
            },
            "stats": stats,
        }

    def get_stats(self, user_id: str = "default") -> dict:
        """Return stats for a user."""
        if user_id not in self._stats and self.db and self.db.is_available:
            record = self.db.get_uncai_stats(user_id)
            if record and record.get("stats"):
                self._stats[user_id] = record["stats"]
        return self._stats.get(user_id, self._new_stats())

    def _build_feedback(self, actual_is_scam: bool, correct: bool, item: dict) -> str:
        if correct and actual_is_scam:
            flags = item.get("red_flags", [])
            if flags:
                return f"Correct. Red flags: {', '.join(flags[:4])}."
            return "Correct. This message shows common scam indicators."
        if correct and not actual_is_scam:
            return "Correct. No clear scam indicators were present."
        if not correct and actual_is_scam:
            flags = item.get("red_flags", [])
            if flags:
                return f"Incorrect. This was a scam. Red flags: {', '.join(flags[:4])}."
            return "Incorrect. This was a scam message."
        return "Incorrect. This message appears legitimate and lacks typical scam indicators."

    def _update_stats(
        self,
        user_id: str,
        correct: bool,
        scam_type: Optional[str],
        reasoning_score: Optional[int],
    ) -> dict:
        stats = self._stats.setdefault(user_id, self._new_stats())
        stats["total"] += 1
        if correct:
            stats["correct"] += 1
            stats["current_streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        else:
            stats["incorrect"] += 1
            stats["current_streak"] = 0

        stats["accuracy"] = round(stats["correct"] / max(1, stats["total"]) * 100, 2)

        if scam_type:
            bucket = stats["by_type"].setdefault(
                scam_type, {"total": 0, "correct": 0, "accuracy": 0.0}
            )
            bucket["total"] += 1
            if correct:
                bucket["correct"] += 1
            bucket["accuracy"] = round(bucket["correct"] / max(1, bucket["total"]) * 100, 2)

        if reasoning_score is not None:
            stats["reasoning_samples"] += 1
            current_avg = stats["avg_reasoning_score"] or 0.0
            count = stats["reasoning_samples"]
            stats["avg_reasoning_score"] = round(
                (current_avg * (count - 1) + reasoning_score) / count,
                2,
            )

        return stats

    @staticmethod
    def _new_stats() -> dict:
        return {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0.0,
            "current_streak": 0,
            "best_streak": 0,
            "avg_reasoning_score": None,
            "reasoning_samples": 0,
            "by_type": {},
        }
