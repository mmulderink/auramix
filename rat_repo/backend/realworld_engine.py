"""Real-world audio transcript analysis engine for ScamGotchi glasses integration."""

import os
import json

from google import genai

from models import GlassesAlert

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Common scam phrases for keyword-based fallback detection
SCAM_INDICATORS = {
    "irs": {"type": "irs_gov", "weight": 0.8},
    "internal revenue": {"type": "irs_gov", "weight": 0.9},
    "warrant for your arrest": {"type": "irs_gov", "weight": 0.9},
    "arrest warrant": {"type": "irs_gov", "weight": 0.85},
    "gift card": {"type": "scam_call", "weight": 0.85},
    "google play card": {"type": "scam_call", "weight": 0.85},
    "itunes card": {"type": "scam_call", "weight": 0.85},
    "social security": {"type": "irs_gov", "weight": 0.7},
    "social security number": {"type": "irs_gov", "weight": 0.85},
    "ssn": {"type": "irs_gov", "weight": 0.8},
    "verify your account": {"type": "phishing", "weight": 0.75},
    "verify your identity": {"type": "phishing", "weight": 0.7},
    "wire transfer": {"type": "scam_call", "weight": 0.8},
    "western union": {"type": "scam_call", "weight": 0.85},
    "moneygram": {"type": "scam_call", "weight": 0.85},
    "bitcoin": {"type": "crypto_investment", "weight": 0.6},
    "cryptocurrency": {"type": "crypto_investment", "weight": 0.6},
    "guaranteed returns": {"type": "crypto_investment", "weight": 0.85},
    "investment opportunity": {"type": "crypto_investment", "weight": 0.7},
    "tech support": {"type": "tech_support", "weight": 0.7},
    "microsoft support": {"type": "tech_support", "weight": 0.85},
    "remote access": {"type": "tech_support", "weight": 0.8},
    "your computer has a virus": {"type": "tech_support", "weight": 0.9},
    "computer is infected": {"type": "tech_support", "weight": 0.9},
    "extended warranty": {"type": "scam_call", "weight": 0.85},
    "you've been selected": {"type": "phishing", "weight": 0.7},
    "you have won": {"type": "phishing", "weight": 0.8},
    "congratulations you've won": {"type": "phishing", "weight": 0.85},
    "act immediately": {"type": "scam_call", "weight": 0.7},
    "act now": {"type": "scam_call", "weight": 0.65},
    "limited time": {"type": "retail", "weight": 0.5},
    "suspended your account": {"type": "phishing", "weight": 0.8},
    "unusual activity": {"type": "phishing", "weight": 0.7},
    "prince": {"type": "phishing", "weight": 0.6},
    "inheritance": {"type": "phishing", "weight": 0.7},
    "beneficiary": {"type": "phishing", "weight": 0.7},
    "pay with gift cards": {"type": "scam_call", "weight": 0.95},
    "do not tell anyone": {"type": "scam_call", "weight": 0.85},
    "keep this between us": {"type": "scam_call", "weight": 0.8},
    "don't hang up": {"type": "scam_call", "weight": 0.75},
    "stay on the line": {"type": "scam_call", "weight": 0.7},
    "this is not a scam": {"type": "scam_call", "weight": 0.9},
    "i'm not a scammer": {"type": "scam_call", "weight": 0.85},
    "qr code": {"type": "qr_code", "weight": 0.5},
    "scan this": {"type": "qr_code", "weight": 0.5},
}


def _keyword_fallback(text: str) -> GlassesAlert:
    """Keyword-based fallback detection for when Gemini is unavailable."""
    text_lower = text.lower()

    best_score = 0.0
    best_type = None
    matched_indicators = []

    for phrase, info in SCAM_INDICATORS.items():
        if phrase in text_lower:
            matched_indicators.append(phrase)
            if info["weight"] > best_score:
                best_score = info["weight"]
                best_type = info["type"]

    threat_detected = best_score >= 0.5

    if threat_detected:
        description = f"Detected {len(matched_indicators)} scam indicator(s): {', '.join(matched_indicators[:5])}"
    else:
        description = "No significant scam indicators detected in the conversation."

    return GlassesAlert(
        alert_type="real_world_audio",
        threat_detected=threat_detected,
        confidence=best_score,
        scam_type=best_type,
        description=description,
        raw_text=text[:500],
        match_score=best_score,
    )


async def analyze_transcript(text: str) -> GlassesAlert:
    """Analyze a phone conversation transcript for scam patterns.

    Uses Gemini for intelligent analysis with a keyword-based fallback.

    Args:
        text: The conversation transcript to analyze.

    Returns:
        A GlassesAlert with threat assessment.
    """
    try:
        prompt = f"""Analyze this phone conversation transcript for scam indicators.

TRANSCRIPT:
\"\"\"{text}\"\"\"

Look for these scam patterns:
- Urgency and pressure tactics ("act now", "limited time", "immediately")
- Threats (arrest, legal action, account suspension)
- Requests for unusual payment methods (gift cards, wire transfer, cryptocurrency)
- Impersonation of authority (IRS, FBI, police, tech companies, banks)
- Social engineering tactics (building rapport, creating false trust)
- Requests for personal information (SSN, bank details, passwords)
- Too-good-to-be-true offers
- Instructions to keep the call secret
- Preventing the victim from hanging up or consulting others

Return ONLY valid JSON:
{{
    "threat_detected": true/false,
    "confidence": 0.0-1.0,
    "scam_type": "phishing|romance|irs_gov|crypto_investment|tech_support|job|retail|real_estate|qr_code|scam_call" or null,
    "description": "Brief description of what was detected and why it's suspicious (or why it seems safe)"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        result_text = response.text.strip()
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            result_text = "\n".join(lines)

        data = json.loads(result_text)

        return GlassesAlert(
            alert_type="real_world_audio",
            threat_detected=data.get("threat_detected", False),
            confidence=max(0.0, min(1.0, float(data.get("confidence", 0.0)))),
            scam_type=data.get("scam_type"),
            description=data.get("description", "Analysis complete."),
            raw_text=text[:500],
            match_score=max(0.0, min(1.0, float(data.get("confidence", 0.0)))),
        )

    except Exception as e:
        print(f"[realworld_engine] Gemini analysis failed: {e}. Using keyword fallback.")
        return _keyword_fallback(text)
