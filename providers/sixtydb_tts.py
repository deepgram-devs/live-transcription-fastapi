"""60db adapter for streaming text-to-speech over WebSocket.

Implements the ``ws/tts`` protocol described in the 60db docs:

    connect (apiKey query param)
      -> server: connecting / connection_established        (ignored handshake)
    create_context  -> server: context_created
    send_text
    flush_context   -> server: audio_chunk* then flush_completed
    close_context   -> server: context_closed

Each ``audio_chunk`` carries base64-encoded audio in the encoding requested via
``audio_config``. We decode and yield the raw bytes so callers receive a plain
stream of audio frames, independent of the wire protocol.
"""
import base64
import json
import uuid
from typing import AsyncIterator

import websockets

from .base import TTSProvider


class SixtyDbTTS(TTSProvider):
    """Streaming text-to-speech backed by the 60db WebSocket API."""

    def __init__(
        self,
        api_key: str,
        ws_url: str,
        voice_id: str,
        sample_rate: int,
        audio_encoding: str,
        speed: float = 1.0,
        stability: int = 50,
        similarity: int = 75,
    ) -> None:
        self._api_key = api_key
        self._ws_url = ws_url
        self._voice_id = voice_id
        self._sample_rate = sample_rate
        self._audio_encoding = audio_encoding
        self._speed = speed
        self._stability = stability
        self._similarity = similarity

    async def synthesize(self, text: str) -> AsyncIterator[bytes]:
        if not self._api_key:
            raise RuntimeError("SIXTYDB_API_KEY is not configured")

        context_id = uuid.uuid4().hex
        url = f"{self._ws_url}?apiKey={self._api_key}"

        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({
                "create_context": {
                    "context_id": context_id,
                    "voice_id": self._voice_id,
                    "audio_config": {
                        "audio_encoding": self._audio_encoding,
                        "sample_rate_hertz": self._sample_rate,
                    },
                    "speed": self._speed,
                    "stability": self._stability,
                    "similarity": self._similarity,
                }
            }))

            # Drain the handshake until the context is confirmed.
            await self._wait_for(ws, "context_created")

            await ws.send(json.dumps({
                "send_text": {"context_id": context_id, "text": text}
            }))
            await ws.send(json.dumps({
                "flush_context": {"context_id": context_id}
            }))

            # Stream audio frames until 60db reports the flush is complete.
            async for raw in ws:
                msg = json.loads(raw)
                if "audio_chunk" in msg:
                    content = msg["audio_chunk"].get("audioContent")
                    if content:
                        yield base64.b64decode(content)
                elif "flush_completed" in msg:
                    break
                elif "error" in msg:
                    raise RuntimeError(f"60db TTS error: {msg['error']}")

            await ws.send(json.dumps({
                "close_context": {"context_id": context_id}
            }))

    @staticmethod
    async def _wait_for(ws, key: str) -> dict:
        """Read messages until one containing ``key`` arrives, ignoring the
        connection handshake frames that precede it."""
        async for raw in ws:
            msg = json.loads(raw)
            if key in msg:
                return msg
            if "error" in msg:
                raise RuntimeError(f"60db TTS error: {msg['error']}")
        raise RuntimeError(f"60db connection closed before '{key}'")
