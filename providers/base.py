"""Provider-neutral interfaces for voice services.

Both directions of the audio pipeline are modelled here so that speech-to-text
and text-to-speech sit behind one consistent boundary:

  - speech-to-text is *push* based: the caller feeds audio chunks and receives
    transcripts via a callback (``STTProvider`` -> ``STTSession``).
  - text-to-speech is *pull* based: the caller hands over text and iterates the
    resulting audio frames (``TTSProvider``).

Adapters translate a specific vendor (Deepgram, 60db, ...) onto these shapes.
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Awaitable, Callable

# Called with each finalized transcript string as it arrives.
OnTranscript = Callable[[str], Awaitable[None]]


class STTSession(ABC):
    """An open streaming speech-to-text session bound to one audio source."""

    @abstractmethod
    def send(self, audio: bytes) -> None:
        """Feed a chunk of raw audio to the provider."""

    @abstractmethod
    async def finish(self) -> None:
        """Signal end-of-audio and release the upstream session."""


class STTProvider(ABC):
    """A streaming speech-to-text provider."""

    @abstractmethod
    async def connect(self, on_transcript: OnTranscript) -> STTSession:
        """Open a session; transcripts are delivered to ``on_transcript``."""


class TTSProvider(ABC):
    """A streaming text-to-speech provider."""

    @abstractmethod
    def synthesize(self, text: str) -> AsyncIterator[bytes]:
        """Yield raw audio frames synthesized from ``text``.

        Implementations are async generators; each yielded ``bytes`` object is a
        decoded audio frame in the provider's configured encoding (e.g. 16-bit
        PCM). The stream ends when synthesis for ``text`` is complete.
        """
