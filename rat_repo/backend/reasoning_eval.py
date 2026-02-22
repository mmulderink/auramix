"""Reasoning evaluation engine using Gemini."""

import os
import json

from google import genai

from models import ScamMessage, ReasoningResult, Personality
from personality import get_dialogue

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CONVINCE_THRESHOLD = 70

RED_FLAG_KEYWORDS = [
    "urgency", "urgent", "immediately", "act now", "limited time",
    "suspicious", "fake", "phishing", "scam",
    "gift card", "wire transfer", "bitcoin", "cryptocurrency", "western union",
    "too good to be true", "guaranteed", "free", "winner", "won",
    "verify", "confirm", "update your", "click here", "link",
    "password", "ssn", "social security", "credit card",
    "threatening", "arrest", "warrant", "legal action", "sue",
    "impersonation", "pretending", "fake company", "spoofed",
    "grammar", "spelling", "typo", "poorly written",
    "generic greeting", "dear customer", "dear user",
    "no contact info", "no phone number", "no address",
    "pressure", "fear", "emotional", "manipulation",
    "unsolicited", "didn't ask", "unexpected", "out of nowhere",
    "domain", "email address", "sender", "from address",
    "attachment", "download", "executable", "zip file",
    "personal information", "data", "identity",
    "romance", "love", "money request", "overseas",
    "investment", "returns", "profit", "guaranteed returns",
]


def _keyword_heuristic(message: ScamMessage, explanation: str) -> tuple[int, list[str]]:
    """Fallback keyword-based scoring when Gemini is unavailable.

    Returns (score, matched_keywords).
    """
    explanation_lower = explanation.lower()
    matched = []

    for keyword in RED_FLAG_KEYWORDS:
        if keyword in explanation_lower:
            matched.append(keyword)

    # Check if explanation mentions actual red flags from the message
    message_flags_mentioned = []
    for flag in message.red_flags:
        if any(word.lower() in explanation_lower for word in flag.split() if len(word) > 3):
            message_flags_mentioned.append(flag)

    # Scoring: base points for length and specificity
    score = 0

    # Length bonus (reasonable explanation should be at least 20 chars)
    if len(explanation) > 20:
        score += 10
    if len(explanation) > 50:
        score += 10
    if len(explanation) > 100:
        score += 10

    # Keyword matches (up to 40 points)
    score += min(40, len(matched) * 8)

    # Actual red flag matches (up to 30 points)
    score += min(30, len(message_flags_mentioned) * 10)

    # Bonus for mentioning specific scam type
    if message.scam_type and message.scam_type.replace("_", " ") in explanation_lower:
        score += 10

    score = min(100, max(0, score))
    all_flags = list(set(matched + message_flags_mentioned))

    return score, all_flags


async def evaluate_reasoning(
    message: ScamMessage,
    explanation: str,
    personality: Personality,
) -> ReasoningResult:
    """Evaluate a player's explanation of why they flagged a message.

    Uses Gemini to score the explanation, with a keyword heuristic fallback.

    Args:
        message: The scam message the player is evaluating.
        explanation: The player's explanation text.
        personality: The current pet personality (for response style).

    Returns:
        A ReasoningResult with score, pet response, and feedback.
    """
    try:
        prompt = f"""You are evaluating a player's explanation for why they think a message is a scam.

THE MESSAGE:
From: {message.sender}
Subject: {message.subject}
Content: {message.content}

ACTUAL RED FLAGS: {json.dumps(message.red_flags)}
ACTUAL SCAM TYPE: {message.scam_type}
ACTUAL TACTICS: {json.dumps(message.tactics)}

PLAYER'S EXPLANATION:
"{explanation}"

Score the explanation from 0-100 based on:
- Did they identify specific red flags? (0-40 points)
- Is their reasoning logical and well-articulated? (0-30 points)
- Did they mention specific suspicious elements from the message? (0-20 points)
- Overall quality - are they clearly reasoning vs just guessing? (0-10 points)

A score of 0 means they gave no useful reasoning at all.
A score of 50 means they identified some issues but missed key red flags.
A score of 70+ means they gave a solid, well-reasoned explanation.
A score of 90+ means they nailed nearly every red flag with clear reasoning.

Return ONLY valid JSON:
{{
    "score": <0-100>,
    "red_flags_mentioned": ["list of red flags the player correctly identified"],
    "feedback": "brief constructive feedback on their reasoning"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines)

        data = json.loads(text)
        score = max(0, min(100, int(data.get("score", 50))))
        red_flags_mentioned = data.get("red_flags_mentioned", [])
        feedback = data.get("feedback", "")

    except Exception as e:
        print(f"[reasoning_eval] Gemini evaluation failed: {e}. Using keyword heuristic.")
        score, red_flags_mentioned = _keyword_heuristic(message, explanation)
        if score >= CONVINCE_THRESHOLD:
            feedback = "Good job identifying the key warning signs!"
        elif score >= 40:
            feedback = "You spotted some issues but missed important red flags. Look more carefully at the sender, urgency cues, and payment requests."
        else:
            feedback = "Your explanation needs more specific details. Try pointing out exact elements that seem suspicious - the sender address, unusual requests, grammar issues, etc."

    convinced = score >= CONVINCE_THRESHOLD

    if convinced:
        pet_response = get_dialogue(personality, "convinced_responses")
    else:
        pet_response = get_dialogue(personality, "not_convinced_responses")

    return ReasoningResult(
        convinced=convinced,
        score=score,
        pet_response=pet_response,
        red_flags_mentioned=red_flags_mentioned,
        feedback=feedback,
    )
