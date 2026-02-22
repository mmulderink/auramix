"""Pet state machine for ScamGotchi."""

from models import PetState, Mood, LivingSituation


CONSEQUENCES: dict[str, dict] = {
    "phishing": {"money": -200, "trust": -10, "street_smarts": 0, "duration": 1},
    "romance": {"money": -500, "trust": 15, "street_smarts": 0, "duration": 3},
    "irs_gov": {"money": -1000, "trust": -5, "street_smarts": 0, "duration": 2},
    "crypto_investment": {"money": -2000, "trust": -20, "street_smarts": 0, "duration": 3},
    "tech_support": {"money": -300, "trust": -15, "street_smarts": 0, "duration": 2},
    "job": {"money": -100, "trust": -10, "street_smarts": 0, "duration": 1},
    "retail": {"money": -150, "trust": -5, "street_smarts": 0, "duration": 1},
    "real_estate": {"money": -5000, "trust": -25, "street_smarts": 0, "duration": 4},
    "qr_code": {"money": -200, "trust": -10, "street_smarts": 0, "duration": 1},
    "scam_call": {"money": -800, "trust": -15, "street_smarts": 0, "duration": 2},
}


def update_living_situation(money: float) -> LivingSituation:
    """Determine living situation based on current money."""
    if money < 100:
        return LivingSituation.CARDBOARD
    elif money < 500:
        return LivingSituation.STUDIO
    elif money < 1500:
        return LivingSituation.APARTMENT
    elif money < 3000:
        return LivingSituation.HOUSE
    else:
        return LivingSituation.MANSION


def compute_mood(state: PetState) -> Mood:
    """Compute the pet's mood based on its current stats."""
    if state.money <= 0:
        return Mood.BROKE
    if state.effect_rounds_remaining > 0 and state.current_effect:
        return Mood.SCAMMED
    if state.scam_streak >= 5:
        return Mood.PARANOID
    if state.scam_streak >= 3:
        return Mood.SUSPICIOUS
    if state.trust < 20:
        return Mood.SCARED
    if state.trust < 35:
        return Mood.SAD
    if state.money < 200:
        return Mood.SCARED
    if state.glasses_alert:
        return Mood.ALERT
    if state.scams_blocked > 5 and state.money > 2000:
        return Mood.THRIVING
    if state.street_smarts > 50 and state.trust > 60:
        return Mood.THRIVING
    if state.trust > 70 and state.money > 1000:
        return Mood.HAPPY
    if state.scams_fallen_for > state.scams_blocked and state.scams_fallen_for > 2:
        return Mood.SAD
    return Mood.HAPPY


def apply_consequence(state: PetState, scam_type: str) -> PetState:
    """Apply the consequence of falling for a scam.

    Mutates money, trust, sets current_effect and effect_rounds_remaining.
    Increments scams_fallen_for and resets scam_streak.
    """
    consequence = CONSEQUENCES.get(scam_type, {"money": -200, "trust": -10, "street_smarts": 0, "duration": 1})

    state.money = max(0, state.money + consequence["money"])
    state.trust = max(0, min(100, state.trust + consequence["trust"]))
    state.street_smarts = max(0, state.street_smarts + consequence["street_smarts"])
    state.current_effect = f"Fell for {scam_type} scam"
    state.effect_rounds_remaining = consequence["duration"]
    state.scams_fallen_for += 1
    state.scam_streak = 0

    state.living_situation = update_living_situation(state.money)
    state.mood = compute_mood(state)

    return state


def apply_correct_identification(state: PetState, was_scam: bool) -> PetState:
    """Apply rewards for correctly identifying a message.

    Args:
        was_scam: True if the message was actually a scam (correctly blocked).
                  False if the message was legit (correctly let through).
    """
    if was_scam:
        state.street_smarts = min(100, state.street_smarts + 5)
        state.trust = min(100, state.trust + 3)
        state.scam_streak += 1
        state.scams_blocked += 1
        # Bonus money for blocking streaks
        if state.scam_streak >= 3:
            state.money += 50 * state.scam_streak
    else:
        # Correctly identified a legit message
        state.trust = min(100, state.trust + 2)
        state.street_smarts = min(100, state.street_smarts + 2)

    state.living_situation = update_living_situation(state.money)
    state.mood = compute_mood(state)

    return state


def apply_false_positive(state: PetState) -> PetState:
    """Apply penalty for flagging a legit message as a scam."""
    state.trust = max(0, state.trust - 5)
    state.scam_streak = max(0, state.scam_streak - 1)

    state.living_situation = update_living_situation(state.money)
    state.mood = compute_mood(state)

    return state


def tick_effects(state: PetState) -> PetState:
    """Decrement active effect rounds. Clear effect when done."""
    if state.effect_rounds_remaining > 0:
        state.effect_rounds_remaining -= 1
        if state.effect_rounds_remaining <= 0:
            state.current_effect = None
            state.effect_rounds_remaining = 0

    state.mood = compute_mood(state)
    return state
