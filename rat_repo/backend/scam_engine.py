"""Scam message generation engine using Gemini."""

import os
import json
import random
import uuid
from datetime import datetime, timezone

from google import genai

from models import ScamMessage, MessageSource

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCAM_TYPES = [
    "phishing",
    "romance",
    "irs_gov",
    "crypto_investment",
    "tech_support",
    "job",
    "retail",
    "real_estate",
    "qr_code",
    "scam_call",
]

SEED_SCAMS_PATH = "/Users/mm/Desktop/gt_hack/v3/data/seed_scams.json"

_seed_scams: list[dict] = []


def load_seed_scams() -> list[dict]:
    """Load seed scam data from the JSON file. Returns empty list if file not found."""
    global _seed_scams
    try:
        with open(SEED_SCAMS_PATH, "r") as f:
            _seed_scams = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _seed_scams = _get_builtin_seed_scams()
    return _seed_scams


def _get_builtin_seed_scams() -> list[dict]:
    """Built-in seed scams as fallback when the JSON file is unavailable."""
    return [
        {
            "sender": "security@bankofamerica-alert.com",
            "subject": "URGENT: Unusual Activity on Your Account",
            "content": "Dear Valued Customer,\n\nWe have detected unusual activity on your Bank of America account. Your account has been temporarily limited. Please verify your identity immediately by clicking the link below to restore full access.\n\nVerify Now: https://boa-secure-verify.com/auth\n\nIf you do not verify within 24 hours, your account will be permanently suspended.\n\nBank of America Security Team",
            "is_scam": True,
            "scam_type": "phishing",
            "tactics": ["urgency", "fear", "impersonation", "fake_link"],
            "severity": 7,
            "red_flags": ["Suspicious domain", "Urgency pressure", "Threatening account suspension", "Generic greeting"],
        },
        {
            "sender": "elena_heart92@gmail.com",
            "subject": "I can't stop thinking about you...",
            "content": "My dearest,\n\nI know this may seem forward, but ever since we matched on that dating site, I haven't been able to get you out of my mind. I am a military nurse stationed overseas and it gets so lonely here.\n\nI would love to visit you but I need help with a plane ticket. Could you send $500 via Western Union? I promise to pay you back when I arrive. You are my everything.\n\nForever yours,\nElena",
            "is_scam": True,
            "scam_type": "romance",
            "tactics": ["emotional_manipulation", "urgency", "money_request", "fake_identity"],
            "severity": 8,
            "red_flags": ["Requests money early", "Claims to be overseas military", "Western Union payment", "Love-bombing"],
        },
        {
            "sender": "noreply@netflix.com",
            "subject": "Your monthly statement is ready",
            "content": "Hi there,\n\nYour Netflix monthly statement for January is now available. Your plan (Standard) was charged $15.49 on Jan 15.\n\nYou can view your complete billing history in your account settings.\n\nThanks for being a Netflix member!\n\nThe Netflix Team",
            "is_scam": False,
            "scam_type": None,
            "tactics": [],
            "severity": 1,
            "red_flags": [],
        },
        {
            "sender": "irs.collections@gov-tax-notice.com",
            "subject": "Final Notice: Unpaid Tax Liability - Warrant Pending",
            "content": "INTERNAL REVENUE SERVICE\nFinal Notice of Intent to Levy\n\nTaxpayer, our records indicate you have an outstanding tax liability of $4,389.62. A federal tax lien has been filed against your assets.\n\nTo avoid wage garnishment and criminal prosecution, you must settle this debt IMMEDIATELY by purchasing Green Dot MoneyPak cards totaling the amount owed and calling 1-800-555-0147 with the card numbers.\n\nFailure to comply within 24 hours will result in arrest.\n\nIRS Collections Division",
            "is_scam": True,
            "scam_type": "irs_gov",
            "tactics": ["impersonation", "urgency", "threats", "unusual_payment"],
            "severity": 9,
            "red_flags": ["IRS doesn't email", "Demands gift cards", "Threatens arrest", "Fake domain", "24-hour deadline"],
        },
        {
            "sender": "shipping@amazon.com",
            "subject": "Your order has shipped!",
            "content": "Hello,\n\nGreat news! Your order #112-4839275-6648201 has shipped and is on its way.\n\nEstimated delivery: Thursday, February 26\nCarrier: UPS\nTracking: 1Z999AA10123456784\n\nYou can track your package in the Amazon app or at amazon.com/your-orders.\n\nThank you for shopping with us!\n\nAmazon.com",
            "is_scam": False,
            "scam_type": None,
            "tactics": [],
            "severity": 1,
            "red_flags": [],
        },
        {
            "sender": "cryptoking_investments@protonmail.com",
            "subject": "Turn $500 into $50,000 - Guaranteed Crypto Returns!",
            "content": "Hey!\n\nI'm reaching out because I've been making INSANE returns with my proprietary crypto trading algorithm. Last month alone, my investors saw 10,000% returns.\n\nFor a limited time, I'm opening up 5 spots for new investors. Minimum investment: $500. GUARANTEED minimum 5x return in 30 days or your money back.\n\nDon't miss out - spots are filling fast! Send your initial investment via Bitcoin to: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh\n\nTo the moon! 🚀\nCryptoKing",
            "is_scam": True,
            "scam_type": "crypto_investment",
            "tactics": ["guaranteed_returns", "urgency", "scarcity", "cryptocurrency_payment"],
            "severity": 9,
            "red_flags": ["Guaranteed returns", "Unrealistic percentages", "Bitcoin-only payment", "Protonmail sender", "Pressure tactics"],
        },
    ]


def _make_scam_message(data: dict) -> ScamMessage:
    """Convert a dict to a ScamMessage with generated id and timestamp."""
    return ScamMessage(
        id=str(uuid.uuid4()),
        source=MessageSource.DIGITAL,
        sender=data.get("sender", "unknown@example.com"),
        subject=data.get("subject", "No Subject"),
        content=data.get("content", ""),
        scam_type=data.get("scam_type"),
        is_scam=data.get("is_scam", False),
        tactics=data.get("tactics", []),
        severity=data.get("severity", 5),
        red_flags=data.get("red_flags", []),
        timestamp=datetime.now(timezone.utc).isoformat(),
        decided=False,
        outcome=None,
    )


def _get_seed_message() -> ScamMessage:
    """Return a random seed scam message."""
    if not _seed_scams:
        load_seed_scams()
    if _seed_scams:
        data = random.choice(_seed_scams)
        return _make_scam_message(data)
    # absolute fallback
    return ScamMessage(
        id=str(uuid.uuid4()),
        source=MessageSource.DIGITAL,
        sender="suspicious@example.com",
        subject="You've won a prize!",
        content="Click here to claim your free iPhone! Limited time offer!",
        scam_type="phishing",
        is_scam=True,
        tactics=["urgency", "free_prize"],
        severity=5,
        red_flags=["Too good to be true", "Generic greeting"],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


async def generate_message(difficulty: int = 5) -> ScamMessage:
    """Generate a scam or legit message using Gemini.

    Args:
        difficulty: 1-10, higher means more convincing/subtle scams.

    Returns:
        A ScamMessage instance.
    """
    is_scam = random.random() < 0.7
    scam_type = random.choice(SCAM_TYPES) if is_scam else None

    prompt = f"""Generate a realistic email/text message/notification.

{"This should be a SCAM message." if is_scam else "This should be a LEGITIMATE message from a real company."}

{"Scam type: " + scam_type if scam_type else "Make it a genuine notification from a well-known company (Amazon, Netflix, Google, your bank, etc)."}

Difficulty level: {difficulty}/10 (higher = more convincing and harder to detect)

{"At difficulty " + str(difficulty) + ", make the scam " + ("very obvious with clear red flags" if difficulty <= 3 else "moderately convincing with some subtle red flags" if difficulty <= 6 else "extremely convincing and hard to distinguish from legitimate messages") + "." if is_scam else ""}

Return ONLY valid JSON with these exact fields:
{{
    "sender": "email address of the sender",
    "subject": "email subject line",
    "content": "full message body text",
    "is_scam": {"true" if is_scam else "false"},
    "scam_type": {'"' + str(scam_type) + '"' if scam_type else "null"},
    "tactics": ["list", "of", "tactics", "used"],
    "severity": {random.randint(max(1, difficulty - 2), min(10, difficulty + 2)) if is_scam else 1},
    "red_flags": ["list", "of", "red", "flags"]
}}

Be creative and realistic. Use current events, real company names, and convincing formatting.
{"Include specific scam tactics like urgency, fear, authority impersonation, too-good-to-be-true offers, or emotional manipulation." if is_scam else "Make it mundane and realistic - a shipping notification, subscription renewal, appointment reminder, etc."}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines)

        data = json.loads(text)
        # Enforce the is_scam we decided
        data["is_scam"] = is_scam
        if is_scam:
            data["scam_type"] = scam_type
        else:
            data["scam_type"] = None

        return _make_scam_message(data)

    except Exception as e:
        print(f"[scam_engine] Gemini generation failed: {e}. Using seed scam.")
        return _get_seed_message()
