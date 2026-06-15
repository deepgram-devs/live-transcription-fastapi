"""Deepgram adapter for streaming speech-to-text.

This wraps the ``deepgram-sdk`` live transcription socket behind the neutral
``STTProvider`` interface. The transcript-extraction logic is exactly what the
original ``main.py`` did inline — it has simply moved behind the abstraction.
"""
from typing import Dict, Optional

from deepgram import Deepgram

from .base import OnTranscript, STTProvider, STTSession

# Mirrors the options the project has always used for the live socket.
DEFAULT_OPTIONS: Dict = {"punctuate": True, "interim_results": False}


class _DeepgramSession(STTSession):
    """Thin wrapper over a connected Deepgram live transcription socket."""

    def __init__(self, socket) -> None:
        self._socket = socket

    def send(self, audio: bytes) -> None:
        self._socket.send(audio)

    async def finish(self) -> None:
        # Best-effort: older SDK builds may not expose finish().
        finish = getattr(self._socket, "finish", None)
        if finish is not None:
            await finish()


class DeepgramSTT(STTProvider):
    """Streaming speech-to-text backed by Deepgram."""

    def __init__(self, api_key: str, options: Optional[Dict] = None) -> None:
        self._client = Deepgram(api_key)
        self._options = options or DEFAULT_OPTIONS

    async def connect(self, on_transcript: OnTranscript) -> STTSession:
        socket = await self._client.transcription.live(self._options)

        async def _handle(data: Dict) -> None:
            if "channel" in data:
                transcript = data["channel"]["alternatives"][0]["transcript"]
                if transcript:
                    await on_transcript(transcript)

        socket.registerHandler(
            socket.event.CLOSE,
            lambda c: print(f"Deepgram connection closed with code {c}."),
        )
        socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, _handle)

        return _DeepgramSession(socket)
