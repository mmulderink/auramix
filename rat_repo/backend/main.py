"""Main FastAPI application for ScamGotchi."""

import os
import sys
import json
import asyncio
from typing import Optional
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    PetState,
    ScamMessage,
    Personality,
    Mood,
    MessageSource,
    GlassesAlert,
)
from personality import get_personality, get_dialogue, PERSONALITIES
from pet_engine import (
    apply_consequence,
    apply_correct_identification,
    apply_false_positive,
    tick_effects,
    compute_mood,
    update_living_situation,
)
from scam_engine import generate_message, load_seed_scams
from reasoning_eval import evaluate_reasoning
from vector_db import vector_store, seed_scam_corpus, search_similar_scams
from neon_db import NeonDB
from realworld_engine import analyze_transcript
from tts import synthesize
from uncai_engine import UncAIEngine

# ─── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="ScamGotchi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global State ──────────────────────────────────────────────────────────────

game_state = PetState()
current_message: Optional[ScamMessage] = None
neon_db = NeonDB()
connected_ws: list[WebSocket] = []
auto_message_task: Optional[asyncio.Task] = None
uncai_engine = UncAIEngine(db=neon_db)


# ─── Request/Response Models ───────────────────────────────────────────────────


class TTSRequest(BaseModel):
    text: str
    personality: str = "chill"


class LeaderboardSubmit(BaseModel):
    user_name: str
    score: int
    street_smarts: int = 0
    scams_blocked: int = 0
    savings_protected: float = 0.0
    personality: str = "chill"


class DemoRequest(BaseModel):
    transcript: Optional[str] = None


class UncAIPracticeRequest(BaseModel):
    scam_type: Optional[str] = None
    source: Optional[str] = None


class UncAISubmitRequest(BaseModel):
    item_id: str
    answer: str
    explanation: Optional[str] = ""
    user_id: Optional[str] = "default"


# ─── Startup / Shutdown ───────────────────────────────────────────────────────


@app.on_event("startup")
async def startup():
    global neon_db
    print("[main] Starting ScamGotchi backend...")

    # Load seed scams
    load_seed_scams()
    print("[main] Seed scams loaded")

    # Initialize Neon DB
    try:
        neon_db.init_tables()
        print(f"[main] Neon DB initialized (available={neon_db.is_available})")
    except Exception as e:
        print(f"[main] Neon DB initialization failed: {e}")

    # Seed vector DB in background
    try:
        await seed_scam_corpus()
        print("[main] Vector DB seeded")
    except Exception as e:
        print(f"[main] Vector DB seeding failed: {e}")

    print("[main] ScamGotchi backend ready!")


@app.on_event("shutdown")
async def shutdown():
    global auto_message_task
    if auto_message_task and not auto_message_task.done():
        auto_message_task.cancel()
    await vector_store.close()
    neon_db.close()
    print("[main] ScamGotchi backend shut down.")


# ─── Helper Functions ──────────────────────────────────────────────────────────


def state_dict() -> dict:
    """Return the current game state as a serializable dict."""
    return game_state.model_dump()


def message_dict(msg: ScamMessage) -> dict:
    """Return a message as a serializable dict (without revealing scam status)."""
    d = msg.model_dump()
    # Don't reveal the answer to the client
    d.pop("is_scam", None)
    d.pop("scam_type", None)
    d.pop("tactics", None)
    d.pop("red_flags", None)
    d.pop("severity", None)
    return d


def full_message_dict(msg: ScamMessage) -> dict:
    """Return the full message dict including scam info (for post-decision reveals)."""
    return msg.model_dump()


async def broadcast(msg_type: str, **fields):
    """Broadcast an event to all connected WebSocket clients.
    Sends {type: msg_type, ...fields} matching the frontend protocol.
    """
    payload = json.dumps({"type": msg_type, **fields})
    disconnected = []
    for ws in connected_ws:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        connected_ws.remove(ws)


async def send(ws: WebSocket, msg_type: str, **fields):
    """Send a message to a single WebSocket client."""
    await ws.send_text(json.dumps({"type": msg_type, **fields}))


# ─── REST Endpoints ───────────────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    """Check status of all services."""
    return {
        "status": "ok",
        "services": {
            "api": True,
            "neon_db": neon_db.is_available,
            "vector_db": vector_store.using_actian or True,  # fallback always works
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "elevenlabs": bool(os.getenv("ELEVENLABS_API_KEY")),
        },
        "game_active": current_message is not None,
        "ws_connections": len(connected_ws),
    }


@app.get("/api/state")
async def get_state():
    """Get the current pet state."""
    return state_dict()


@app.get("/api/personalities")
async def list_personalities():
    """List all available personalities."""
    result = []
    for p_enum, profile in PERSONALITIES.items():
        result.append({
            "id": p_enum.value,
            "name": profile["name"],
            "emoji": profile["emoji"],
            "style": profile["style"],
        })
    return result


@app.get("/api/message/new")
async def new_message():
    """Generate a new scam/legit message."""
    global current_message
    current_message = await generate_message(difficulty=5)
    tick_effects(game_state)
    return message_dict(current_message)


@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    """Synthesize text to speech."""
    try:
        audio_bytes = await synthesize(req.text, req.personality)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except RuntimeError as e:
        return {"error": str(e)}


@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get the leaderboard."""
    return neon_db.get_leaderboard(limit=20)


@app.post("/api/leaderboard")
async def submit_to_leaderboard(req: LeaderboardSubmit):
    """Submit a score to the leaderboard."""
    result = neon_db.submit_score(
        user_name=req.user_name,
        score=req.score,
        street_smarts=req.street_smarts,
        scams_blocked=req.scams_blocked,
        savings_protected=req.savings_protected,
        personality=req.personality,
    )
    if result:
        return {"success": True, "entry": result}
    return {"success": False, "error": "Failed to submit score"}


@app.get("/api/vector/search")
async def vector_search(q: str = Query(..., description="Search query")):
    """Semantic search for similar scams."""
    results = await search_similar_scams(q, top_k=5)
    return {"query": q, "results": results}


@app.get("/api/vector/stats")
async def vector_stats():
    """Get vector collection stats."""
    stats = await vector_store.get_stats("scam_corpus")
    return stats


@app.post("/api/uncai/practice")
async def uncai_practice(req: UncAIPracticeRequest = None):
    """Get a practice item for UncAI training."""
    scam_type = req.scam_type if req else None
    source = req.source if req else None
    item = uncai_engine.get_practice_item(scam_type=scam_type, source=source)
    if not item:
        return {"success": False, "error": "No practice items available"}
    return {"success": True, "item": item}


@app.post("/api/uncai/submit")
async def uncai_submit(req: UncAISubmitRequest):
    """Submit an answer for a practice item and return feedback."""
    result = await uncai_engine.evaluate_answer(
        item_id=req.item_id,
        answer=req.answer,
        explanation=req.explanation or "",
        user_id=req.user_id or "default",
    )
    if not result:
        return {"success": False, "error": "Practice item not found"}
    return {"success": True, **result}


@app.get("/api/uncai/stats")
async def uncai_stats(user_id: str = Query("default", description="User id")):
    """Get UncAI performance stats."""
    return {"success": True, "stats": uncai_engine.get_stats(user_id=user_id)}


@app.post("/api/demo/qr")
async def demo_qr(req: DemoRequest = None):
    """Trigger a demo QR code scam scenario."""
    global current_message

    current_message = ScamMessage(
        id="demo-qr-001",
        source=MessageSource.GLASSES,
        sender="QR Code Scan",
        subject="Scanned QR Code - Parking Payment",
        content=(
            "You scanned a QR code on a parking meter. It redirects to: "
            "https://c1ty-parking-pay.com/meter/7294\n\n"
            "The page asks you to enter your credit card information to pay "
            "a $2.50 parking fee. The page looks official with city logos, "
            "but the URL doesn't match the official city website.\n\n"
            "Enter your payment details to avoid a $75 parking ticket."
        ),
        scam_type="qr_code",
        is_scam=True,
        tactics=["fake_website", "urgency", "impersonation", "small_amount_trust"],
        severity=6,
        red_flags=[
            "Suspicious URL not matching city domain",
            "QR code on public infrastructure could be tampered",
            "Urgency with parking ticket threat",
            "Asking for full credit card for small amount",
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    await broadcast("new_message", message=message_dict(current_message))
    await broadcast("real_world_alert",
        alert={"alert_type": "qr_code", "threat_detected": True, "confidence": 0.85,
               "scam_type": "qr_code",
               "description": "Suspicious QR code detected! URL doesn't match any known city parking systems.",
               "raw_text": "", "match_score": 0.85},
        pet_warning=get_dialogue(game_state.personality, "glasses_warnings"),
        pet_state=state_dict(),
    )

    return {"success": True, "message": message_dict(current_message)}


@app.post("/api/demo/call")
async def demo_call(req: DemoRequest = None):
    """Trigger a demo scam call scenario."""
    global current_message

    transcript = (
        req.transcript
        if req and req.transcript
        else (
            "Hello, this is Agent Johnson from the Internal Revenue Service. "
            "We have detected a serious issue with your tax returns from 2023. "
            "There is a warrant being issued for your arrest due to unpaid taxes "
            "totaling $4,389. However, if you act immediately, we can resolve this "
            "today. You will need to purchase Google Play gift cards totaling the "
            "amount owed and read me the card numbers. This is time-sensitive - "
            "if you hang up, officers will be dispatched to your location. "
            "Do not tell anyone about this call as it is under federal investigation."
        )
    )

    alert = await analyze_transcript(transcript)

    current_message = ScamMessage(
        id="demo-call-001",
        source=MessageSource.GLASSES,
        sender="Incoming Call: +1 (202) 555-0147",
        subject="Urgent Call - Claims to be IRS",
        content=f"LIVE CALL TRANSCRIPT:\n\n{transcript}",
        scam_type=alert.scam_type or "scam_call",
        is_scam=True,
        tactics=["impersonation", "urgency", "threats", "unusual_payment", "isolation"],
        severity=9,
        red_flags=[
            "IRS does not call demanding immediate payment",
            "Government agencies don't accept gift cards",
            "Threatening arrest over the phone",
            "Demanding secrecy about the call",
            "Creating extreme urgency",
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    game_state.glasses_connected = True
    game_state.glasses_alert = alert.description

    await broadcast("new_message", message=message_dict(current_message))
    await broadcast("real_world_alert",
        alert=alert.model_dump(),
        pet_warning=get_dialogue(game_state.personality, "glasses_warnings"),
        pet_state=state_dict(),
    )
    await broadcast("state_update", pet_state=state_dict())

    return {
        "success": True,
        "message": message_dict(current_message),
        "alert": alert.model_dump(),
    }


# ─── WebSocket: Game ──────────────────────────────────────────────────────────


@app.websocket("/ws/game")
async def ws_game(websocket: WebSocket):
    """Main game WebSocket connection."""
    global current_message, auto_message_task

    await websocket.accept()
    connected_ws.append(websocket)

    # Send init message
    personalities_list = []
    for p_enum, profile in PERSONALITIES.items():
        personalities_list.append({
            "id": p_enum.value,
            "name": profile["name"],
            "emoji": profile["emoji"],
            "style": profile["style"],
        })

    await send(websocket, "init",
        pet_state=state_dict(),
        personalities=personalities_list,
    )

    # Send an initial message right away so the inbox isn't empty
    if current_message is None:
        try:
            await _send_auto_message()
        except Exception as e:
            print(f"[ws_game] Failed to generate initial message: {e}")

    # Start auto-message background task if not running
    if auto_message_task is None or auto_message_task.done():
        auto_message_task = asyncio.create_task(_auto_message_loop())

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await send(websocket, "error", message="Invalid JSON")
                continue

            msg_type = msg.get("type")

            if msg_type == "player_action":
                await _handle_player_action(websocket, msg)

            elif msg_type == "player_explain":
                await _handle_player_explain(websocket, msg)

            elif msg_type == "change_personality":
                await _handle_change_personality(websocket, msg)

            elif msg_type == "request_message":
                await _handle_request_message(websocket)

            elif msg_type == "demo_qr":
                await demo_qr()

            elif msg_type == "demo_call":
                transcript = msg.get("transcript")
                await demo_call(DemoRequest(transcript=transcript) if transcript else None)

            else:
                await send(websocket, "error", message=f"Unknown type: {msg_type}")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[ws_game] Error: {e}")
    finally:
        if websocket in connected_ws:
            connected_ws.remove(websocket)


async def _handle_player_action(websocket: WebSocket, msg: dict):
    """Handle player_action: player says 'scam' or 'legit'."""
    global current_message, game_state

    if not current_message:
        await send(websocket, "error", message="No current message to judge")
        return

    player_says = msg.get("action", "").lower()  # "scam" or "legit"

    if player_says == "scam" and current_message.is_scam:
        # Correct! But pet pushes back and wants an explanation first
        scam_type = current_message.scam_type or "phishing"
        pushback = get_dialogue(game_state.personality, "pushback", scam_type)

        await send(websocket, "pet_pushback",
            message_id=current_message.id,
            dialogue=pushback,
            pet_state=state_dict(),
        )

    elif player_says == "legit" and current_message.is_scam:
        # Wrong! Player thought scam was legit - apply consequences
        scam_type = current_message.scam_type or "phishing"
        consequence_reaction = get_dialogue(game_state.personality, "scam_consequence_reactions")

        apply_consequence(game_state, scam_type)
        current_message.decided = True
        current_message.outcome = "fell_for_scam"

        # Log to Neon
        neon_db.log_scam(
            user_id="default",
            scam_type=scam_type,
            is_scam=True,
            player_said_scam=False,
            reasoning_score=0,
            outcome="fell_for_scam",
        )

        money_lost = abs(({"phishing": 200, "romance": 500, "irs_gov": 1000, "crypto_investment": 2000,
              "tech_support": 300, "job": 100, "retail": 150, "real_estate": 5000,
              "qr_code": 200, "scam_call": 800}).get(scam_type, 200))
        await broadcast("scam_consequence",
            message_id=current_message.id,
            scam_type=scam_type,
            money_lost=money_lost,
            dialogue=consequence_reaction,
            pet_state=state_dict(),
        )

        current_message = None

    elif player_says == "legit" and not current_message.is_scam:
        # Correct! Legit message correctly identified as legit
        apply_correct_identification(game_state, was_scam=False)
        current_message.decided = True
        current_message.outcome = "legit_correct"

        neon_db.log_scam(
            user_id="default",
            scam_type=None,
            is_scam=False,
            player_said_scam=False,
            reasoning_score=100,
            outcome="legit_correct",
        )

        await broadcast("legit_correct",
            message_id=current_message.id,
            pet_state=state_dict(),
        )

        current_message = None

    elif player_says == "scam" and not current_message.is_scam:
        # Wrong! Player flagged a legit message as scam
        apply_false_positive(game_state)
        current_message.decided = True
        current_message.outcome = "false_positive"

        neon_db.log_scam(
            user_id="default",
            scam_type=None,
            is_scam=False,
            player_said_scam=True,
            reasoning_score=0,
            outcome="false_positive",
        )

        await broadcast("false_positive",
            message_id=current_message.id,
            pet_state=state_dict(),
        )

        current_message = None

    else:
        await websocket.send_text(json.dumps({
            "event": "error",
            "data": {"message": "Invalid decision. Send 'scam' or 'legit'."},
        }))


async def _handle_player_explain(websocket: WebSocket, msg: dict):
    """Handle player_explain: evaluate the player's reasoning."""
    global current_message, game_state

    if not current_message:
        await send(websocket, "error", message="No current message to explain about")
        return

    explanation = msg.get("explanation", "")

    if not explanation.strip():
        await send(websocket, "error", message="Please provide an explanation")
        return

    # Evaluate reasoning using Gemini
    result = await evaluate_reasoning(
        message=current_message,
        explanation=explanation,
        personality=game_state.personality,
    )

    scam_type = current_message.scam_type or "phishing"

    if result.convinced:
        # Pet is convinced - scam blocked!
        apply_correct_identification(game_state, was_scam=True)
        current_message.decided = True
        current_message.outcome = "scam_blocked"

        neon_db.log_scam(
            user_id="default",
            scam_type=scam_type,
            is_scam=True,
            player_said_scam=True,
            reasoning_score=result.score,
            outcome="scam_blocked",
        )

        await broadcast("scam_blocked",
            message_id=current_message.id,
            result={"convinced": True, "score": result.score,
                    "pet_response": result.pet_response,
                    "red_flags_mentioned": result.red_flags_mentioned,
                    "feedback": result.feedback},
            pet_state=state_dict(),
        )

        current_message = None

    else:
        # Pet is NOT convinced - reasoning failed, consequence applies
        apply_consequence(game_state, scam_type)
        current_message.decided = True
        current_message.outcome = "reasoning_failed"

        neon_db.log_scam(
            user_id="default",
            scam_type=scam_type,
            is_scam=True,
            player_said_scam=True,
            reasoning_score=result.score,
            outcome="reasoning_failed",
        )

        await broadcast("reasoning_failed",
            message_id=current_message.id,
            result={"convinced": False, "score": result.score,
                    "pet_response": result.pet_response,
                    "red_flags_mentioned": result.red_flags_mentioned,
                    "feedback": result.feedback},
            pet_state=state_dict(),
        )

        current_message = None


async def _handle_change_personality(websocket: WebSocket, msg: dict):
    """Handle change_personality action."""
    global game_state

    new_personality = msg.get("personality", "chill").lower()
    try:
        game_state.personality = Personality(new_personality)
    except ValueError:
        await websocket.send_text(json.dumps({
            "event": "error",
            "data": {"message": f"Unknown personality: {new_personality}"},
        }))
        return

    profile = get_personality(game_state.personality)
    idle = get_dialogue(game_state.personality, "idle_chatter")

    await broadcast("personality_changed", pet_state=state_dict())


async def _handle_request_message(websocket: WebSocket):
    """Handle request_message: generate and send a new message."""
    global current_message

    current_message = await generate_message(difficulty=5)
    tick_effects(game_state)

    await broadcast("new_message", message=message_dict(current_message))
    await broadcast("state_update", pet_state=state_dict())


async def _auto_message_loop():
    """Background task that sends a new message every 30 seconds."""
    while True:
        await asyncio.sleep(30)
        if connected_ws:
            try:
                await _send_auto_message()
            except Exception as e:
                print(f"[auto_message] Error: {e}")


async def _send_auto_message():
    """Generate and broadcast a new message."""
    global current_message
    current_message = await generate_message(difficulty=5)
    tick_effects(game_state)
    await broadcast("new_message", message=message_dict(current_message))
    await broadcast("state_update", pet_state=state_dict())


# ─── WebSocket: Audio ─────────────────────────────────────────────────────────


@app.websocket("/ws/audio")
async def ws_audio(websocket: WebSocket):
    """Audio WebSocket for real-world glasses integration.

    Receives text transcripts (as JSON) or binary audio chunks.
    Sends back JSON alerts and binary TTS audio.
    """
    await websocket.accept()

    try:
        while True:
            # Try to receive either text or bytes
            data = await websocket.receive()

            if "text" in data:
                # JSON text message with transcript
                try:
                    msg = json.loads(data["text"])
                    transcript = msg.get("transcript", "")

                    if not transcript:
                        await websocket.send_text(json.dumps({
                            "event": "error",
                            "data": {"message": "No transcript provided"},
                        }))
                        continue

                    # Analyze the transcript
                    alert = await analyze_transcript(transcript)

                    # Send alert JSON
                    await websocket.send_text(json.dumps({
                        "event": "glasses_alert",
                        "data": alert.model_dump(),
                    }))

                    # If threat detected, generate and send TTS warning
                    if alert.threat_detected:
                        warning = get_dialogue(game_state.personality, "glasses_warnings")
                        try:
                            audio_bytes = await synthesize(warning, game_state.personality.value)
                            # Send TTS audio as binary
                            await websocket.send_bytes(audio_bytes)
                        except Exception as e:
                            print(f"[ws_audio] TTS failed: {e}")

                        # Update game state
                        game_state.glasses_connected = True
                        game_state.glasses_alert = alert.description
                        if alert.threat_detected:
                            game_state.realworld_catches += 1
                        game_state.mood = compute_mood(game_state)

                        # Broadcast state update to game websockets
                        await broadcast("state_update", state_dict())
                        await broadcast("glasses_alert", alert.model_dump())

                except json.JSONDecodeError:
                    # Treat as raw transcript text
                    alert = await analyze_transcript(data["text"])
                    await websocket.send_text(json.dumps({
                        "event": "glasses_alert",
                        "data": alert.model_dump(),
                    }))

            elif "bytes" in data:
                # Binary audio data - for now, send back an acknowledgment
                # In production, this would go through speech-to-text first
                await websocket.send_text(json.dumps({
                    "event": "audio_received",
                    "data": {
                        "bytes_received": len(data["bytes"]),
                        "message": "Audio received. For full analysis, please send a text transcript.",
                    },
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[ws_audio] Error: {e}")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
