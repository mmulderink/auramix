"""Text-to-speech engine with ElevenLabs, edge-tts, and gTTS fallback chain."""

import os
import io
import asyncio
from typing import Optional

import httpx
import edge_tts
from gtts import gTTS

from models import Personality

# Voice mappings for each TTS engine
EDGE_TTS_VOICES = {
    Personality.ABUELA: "es-MX-DaliaNeural",
    Personality.WATCHDOG: "en-US-GuyNeural",
    Personality.CHILL: "en-US-JennyNeural",
    Personality.AGENT: "en-GB-RyanNeural",
    Personality.ORACLE: "en-US-AriaNeural",
}

ELEVENLABS_VOICE_IDS = {
    Personality.ABUELA: os.getenv("ELEVENLABS_ABUELA_ID", ""),
    Personality.WATCHDOG: os.getenv("ELEVENLABS_WATCHDOG_ID", ""),
    Personality.CHILL: os.getenv("ELEVENLABS_CHILL_ID", ""),
    Personality.AGENT: os.getenv("ELEVENLABS_AGENT_ID", ""),
    Personality.ORACLE: os.getenv("ELEVENLABS_ORACLE_ID", ""),
}

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")


def _get_personality_enum(personality: str) -> Personality:
    """Convert a personality string to a Personality enum."""
    try:
        return Personality(personality.lower())
    except ValueError:
        return Personality.CHILL


async def _try_elevenlabs(text: str, personality: Personality) -> Optional[bytes]:
    """Try to synthesize speech using ElevenLabs API.

    Returns audio bytes (mp3) or None on failure.
    """
    api_key = ELEVENLABS_API_KEY
    if not api_key:
        return None

    voice_id = ELEVENLABS_VOICE_IDS.get(personality, "")
    if not voice_id:
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                url,
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
            )
            if response.status_code == 200:
                return response.content
            else:
                print(f"[tts] ElevenLabs returned status {response.status_code}: {response.text[:200]}")
                return None
    except Exception as e:
        print(f"[tts] ElevenLabs failed: {e}")
        return None


async def _try_edge_tts(text: str, personality: Personality) -> Optional[bytes]:
    """Try to synthesize speech using edge-tts.

    Returns audio bytes (mp3) or None on failure.
    """
    voice = EDGE_TTS_VOICES.get(personality, "en-US-JennyNeural")

    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_chunks = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        if audio_chunks:
            return b"".join(audio_chunks)
        return None
    except Exception as e:
        print(f"[tts] edge-tts failed: {e}")
        return None


def _try_gtts(text: str, personality: Personality) -> Optional[bytes]:
    """Try to synthesize speech using gTTS (Google Text-to-Speech).

    Returns audio bytes (mp3) or None on failure.
    """
    try:
        lang = "es" if personality == Personality.ABUELA else "en"
        tts = gTTS(text=text, lang=lang, slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        print(f"[tts] gTTS failed: {e}")
        return None


async def synthesize(text: str, personality: str) -> bytes:
    """Synthesize text to speech using the fallback chain: ElevenLabs -> edge-tts -> gTTS.

    Args:
        text: The text to speak.
        personality: The personality name string.

    Returns:
        Audio bytes in audio/mpeg format.

    Raises:
        RuntimeError: If all TTS engines fail.
    """
    personality_enum = _get_personality_enum(personality)

    # Truncate very long text to avoid TTS issues
    if len(text) > 1000:
        text = text[:997] + "..."

    # Try ElevenLabs first
    audio = await _try_elevenlabs(text, personality_enum)
    if audio:
        print(f"[tts] Used ElevenLabs for {personality}")
        return audio

    # Try edge-tts
    audio = await _try_edge_tts(text, personality_enum)
    if audio:
        print(f"[tts] Used edge-tts for {personality}")
        return audio

    # Try gTTS (synchronous, run in executor)
    loop = asyncio.get_event_loop()
    audio = await loop.run_in_executor(None, _try_gtts, text, personality_enum)
    if audio:
        print(f"[tts] Used gTTS for {personality}")
        return audio

    raise RuntimeError("All TTS engines failed")
