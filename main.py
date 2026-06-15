from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import config
from providers.deepgram_stt import DeepgramSTT
from providers.sixtydb_tts import SixtyDbTTS

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Voice providers, wired once and used through their neutral interfaces.
stt_provider = DeepgramSTT(config.DEEPGRAM_API_KEY)
tts_provider = SixtyDbTTS(
    api_key=config.SIXTYDB_API_KEY,
    ws_url=config.SIXTYDB_WS_URL,
    voice_id=config.SIXTYDB_VOICE_ID,
    sample_rate=config.SIXTYDB_SAMPLE_RATE,
    audio_encoding=config.SIXTYDB_AUDIO_ENCODING,
    speed=config.SIXTYDB_SPEED,
    stability=config.SIXTYDB_STABILITY,
    similarity=config.SIXTYDB_SIMILARITY,
)

# Sentinel sent over /speak to mark the end of one synthesized utterance.
TTS_END_MARKER = "__end__"


@app.get("/", response_class=HTMLResponse)
def get(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "sample_rate": config.SIXTYDB_SAMPLE_RATE},
    )


@app.websocket("/listen")
async def listen(websocket: WebSocket):
    """Speech-to-text: browser streams mic audio in, transcripts stream out."""
    await websocket.accept()

    try:
        session = await stt_provider.connect(websocket.send_text)

        while True:
            data = await websocket.receive_bytes()
            session.send(data)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        raise Exception(f"Could not process audio: {e}")
    finally:
        await websocket.close()


@app.websocket("/speak")
async def speak(websocket: WebSocket):
    """Text-to-speech: browser sends text, raw audio frames stream back.

    Audio frames are sent as binary messages; a trailing text marker signals the
    end of each utterance so the client knows when to play it back.
    """
    await websocket.accept()

    try:
        while True:
            text = await websocket.receive_text()
            if not text.strip():
                continue

            async for frame in tts_provider.synthesize(text):
                await websocket.send_bytes(frame)

            await websocket.send_text(TTS_END_MARKER)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        raise Exception(f"Could not synthesize speech: {e}")
    finally:
        await websocket.close()
