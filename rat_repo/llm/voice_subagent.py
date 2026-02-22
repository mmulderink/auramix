"""
Voice Subagent
Generates text-to-speech audio and plays it alongside animations.
"""

import os
import sys
import time
import subprocess
import threading
from typing import Optional
from openai import OpenAI


class VoiceSubagent:
    """Subagent responsible for text-to-speech and playback."""

    def __init__(self, api_key: str, model: str, voice: str,
                 output_dir: str, max_cache_bytes: int = 100 * 1024 * 1024):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.voice = voice
        self.output_dir = output_dir
        self.max_cache_bytes = max_cache_bytes
        self._counter = 0
        self._warned_no_playback = False
        self._debug = os.getenv("LLM_TTS_DEBUG", "false").lower() in ["1", "true", "yes"]
        self._player = os.getenv("LLM_TTS_PLAYER", "simpleaudio").lower()
        self._play_delay_sec = float(os.getenv("LLM_TTS_PLAY_DELAY_MS", "500")) / 1000.0
        self._active_playbacks = []

        os.makedirs(self.output_dir, exist_ok=True)

    def generate_and_play(self, text: str, emotion: Optional[str] = None,
                          start_event: Optional[threading.Event] = None):
        """Generate TTS audio and play it asynchronously when possible."""
        if not text:
            if start_event:
                start_event.set()
            return

        file_path = self._next_file_path()

        try:
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format="wav"
            )
            response.write_to_file(file_path)
            if self._debug:
                try:
                    size_bytes = os.path.getsize(file_path)
                    print(f"Voice Subagent: wrote {size_bytes} bytes to {file_path}")
                except OSError as exc:
                    print(f"Voice Subagent: could not stat audio file: {exc}")
        except Exception as exc:
            print(f"Voice Subagent Error: {exc}")
            return

        self._play_audio(file_path, start_event)
        self._cleanup_if_needed()

    def _next_file_path(self) -> str:
        timestamp = int(time.time() * 1000)
        self._counter += 1
        filename = f"tts_{timestamp}_{self._counter}.wav"
        return os.path.join(self.output_dir, filename)

    def _play_audio(self, file_path: str, start_event: Optional[threading.Event]):
        if self._play_delay_sec > 0:
            time.sleep(self._play_delay_sec)
        if sys.platform.startswith("win"):
            if self._player == "powershell":
                self._play_audio_powershell(file_path, start_event)
                return
            if self._player == "winsound":
                self._play_audio_winsound(file_path, start_event)
                return

            self._play_audio_simpleaudio(file_path, start_event)
            return

        if not self._warned_no_playback:
            print("Voice Subagent: audio playback not configured for this OS.")
            self._warned_no_playback = True
        if start_event:
            start_event.set()

    def _play_audio_winsound(self, file_path: str, start_event: Optional[threading.Event]):
        import winsound
        if self._debug:
            print(f"Voice Subagent: playing audio via winsound: {file_path}")

        flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
        winsound.PlaySound(file_path, flags)
        if start_event:
            start_event.set()

    def _play_audio_powershell(self, file_path: str, start_event: Optional[threading.Event]):
        if self._debug:
            print(f"Voice Subagent: playing audio via PowerShell: {file_path}")

        safe_path = file_path.replace("'", "''")
        command = (
            f"$player = New-Object System.Media.SoundPlayer '{safe_path}'; "
            f"$player.PlaySync()"
        )

        try:
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if start_event:
                start_event.set()
        except Exception as exc:
            print(f"Voice Subagent playback error: {exc}")
            if start_event:
                start_event.set()

    def _play_audio_simpleaudio(self, file_path: str, start_event: Optional[threading.Event]):
        try:
            import simpleaudio as sa
        except Exception as exc:
            print(f"Voice Subagent: simpleaudio unavailable: {exc}")
            if start_event:
                start_event.set()
            return

        try:
            if self._debug:
                print(f"Voice Subagent: playing audio via simpleaudio: {file_path}")
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            self._active_playbacks.append(play_obj)
            self._cleanup_playbacks()
            if start_event:
                start_event.set()
        except Exception as exc:
            print(f"Voice Subagent playback error: {exc}")
            if start_event:
                start_event.set()

    def _cleanup_playbacks(self):
        if not self._active_playbacks:
            return

        self._active_playbacks = [
            playback for playback in self._active_playbacks
            if playback.is_playing()
        ]

    def _cleanup_if_needed(self):
        if self.max_cache_bytes <= 0:
            return

        try:
            entries = []
            total_size = 0
            for name in os.listdir(self.output_dir):
                if not name.lower().endswith(".wav"):
                    continue
                path = os.path.join(self.output_dir, name)
                try:
                    stat = os.stat(path)
                except FileNotFoundError:
                    continue
                total_size += stat.st_size
                entries.append((stat.st_mtime, path, stat.st_size))

            if total_size <= self.max_cache_bytes:
                return

            entries.sort(key=lambda item: item[0])
            for _, path, size in entries:
                try:
                    os.remove(path)
                    total_size -= size
                except FileNotFoundError:
                    continue

                if total_size <= self.max_cache_bytes:
                    break
        except Exception as exc:
            print(f"Voice Subagent cleanup error: {exc}")
