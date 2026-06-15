"""Voice provider abstractions and adapters.

This package defines a small, transport-agnostic boundary for voice services:

  - ``STTProvider`` / ``STTSession`` for streaming speech-to-text
  - ``TTSProvider``                 for streaming text-to-speech

Concrete adapters (Deepgram for STT, 60db for TTS) implement these interfaces
so that ``main.py`` depends only on the abstraction and never on a specific
vendor SDK or wire protocol.
"""
from .base import STTProvider, STTSession, TTSProvider

__all__ = ["STTProvider", "STTSession", "TTSProvider"]
