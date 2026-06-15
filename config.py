"""Central configuration loaded from the environment (.env file).

All provider credentials and tunables live here so that the rest of the app
never reads os.environ directly. This keeps the provider wiring in main.py
declarative and makes it obvious what needs to be configured.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# --- Deepgram (speech-to-text) ---------------------------------------------
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# --- 60db (text-to-speech) -------------------------------------------------
SIXTYDB_API_KEY = os.getenv("SIXTYDB_API_KEY")
# WebSocket endpoint for the 60db streaming TTS service.
SIXTYDB_WS_URL = os.getenv("SIXTYDB_WS_URL", "wss://api.60db.ai/ws/tts")
SIXTYDB_VOICE_ID = os.getenv("SIXTYDB_VOICE_ID", "default-voice")
# Audio the browser knows how to play back: 16-bit signed PCM, mono.
SIXTYDB_AUDIO_ENCODING = os.getenv("SIXTYDB_AUDIO_ENCODING", "LINEAR16")
SIXTYDB_SAMPLE_RATE = int(os.getenv("SIXTYDB_SAMPLE_RATE", "24000"))
# Voice tunables (see 60db docs for ranges).
SIXTYDB_SPEED = float(os.getenv("SIXTYDB_SPEED", "1.0"))        # 0.5 - 2.0
SIXTYDB_STABILITY = int(os.getenv("SIXTYDB_STABILITY", "50"))   # 0 - 100
SIXTYDB_SIMILARITY = int(os.getenv("SIXTYDB_SIMILARITY", "75")) # 0 - 100
