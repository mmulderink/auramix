"""Pydantic models for ScamGotchi."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Personality(str, Enum):
    ABUELA = "abuela"
    WATCHDOG = "watchdog"
    CHILL = "chill"
    AGENT = "agent"
    ORACLE = "oracle"


class Mood(str, Enum):
    HAPPY = "happy"
    SUSPICIOUS = "suspicious"
    IN_LOVE = "in_love"
    SCARED = "scared"
    BROKE = "broke"
    SCAMMED = "scammed"
    THRIVING = "thriving"
    ALERT = "alert"
    SAD = "sad"
    PARANOID = "paranoid"


class LivingSituation(str, Enum):
    CARDBOARD = "cardboard"
    STUDIO = "studio"
    APARTMENT = "apartment"
    HOUSE = "house"
    MANSION = "mansion"


class MessageSource(str, Enum):
    DIGITAL = "digital"
    GLASSES = "glasses"


class PetState(BaseModel):
    name: str = "ScamGotchi"
    personality: Personality = Personality.CHILL
    money: float = Field(default=1000.0)
    trust: int = Field(default=50)
    street_smarts: int = Field(default=0)
    mood: Mood = Mood.HAPPY
    living_situation: LivingSituation = LivingSituation.APARTMENT
    glasses_connected: bool = False
    glasses_alert: Optional[str] = None
    scam_streak: int = 0
    scams_blocked: int = 0
    scams_fallen_for: int = 0
    realworld_catches: int = 0
    current_effect: Optional[str] = None
    effect_rounds_remaining: int = 0


class ScamMessage(BaseModel):
    id: str
    source: MessageSource = MessageSource.DIGITAL
    sender: str
    subject: str
    content: str
    scam_type: Optional[str] = None
    is_scam: bool
    tactics: list[str] = Field(default_factory=list)
    severity: int = Field(default=5, ge=1, le=10)
    red_flags: list[str] = Field(default_factory=list)
    timestamp: str = ""
    decided: bool = False
    outcome: Optional[str] = None


class GlassesAlert(BaseModel):
    alert_type: str
    threat_detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    scam_type: Optional[str] = None
    description: str
    raw_text: str
    match_score: float = Field(default=0.0)


class ReasoningResult(BaseModel):
    convinced: bool
    score: int = Field(ge=0, le=100)
    pet_response: str
    red_flags_mentioned: list[str] = Field(default_factory=list)
    feedback: str
