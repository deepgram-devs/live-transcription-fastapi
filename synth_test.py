import asyncio, json, urllib.request, wave, config
from providers.sixtydb_tts import SixtyDbTTS

# 1) fetch voices, choose an English one
req = urllib.request.Request("https://api.60db.ai/voices",
    headers={"Authorization": f"Bearer {config.SIXTYDB_API_KEY}"})
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read().decode())["data"]
voices = (data.get("built_in_voices") or []) + (data.get("cloned_voices") or [])

def lang(v): return (v.get("labels") or {}).get("language")
english = [v for v in voices if lang(v) == "en"]
chosen = (english or voices)[0]
vid, name = chosen["voice_id"], chosen["name"]
print(f"CHOSEN voice -> name={name!r}  language={lang(chosen)!r}  voice_id={vid}")

# 2) synthesize via the project's provider, overriding only the voice id
tts = SixtyDbTTS(
    api_key=config.SIXTYDB_API_KEY, ws_url=config.SIXTYDB_WS_URL, voice_id=vid,
    sample_rate=config.SIXTYDB_SAMPLE_RATE, audio_encoding=config.SIXTYDB_AUDIO_ENCODING,
    speed=config.SIXTYDB_SPEED, stability=config.SIXTYDB_STABILITY, similarity=config.SIXTYDB_SIMILARITY,
)

async def run():
    pcm = bytearray()
    async for frame in tts.synthesize("Hello! This is a test of 60db text to speech, running on your machine."):
        pcm += frame
    return bytes(pcm)

pcm = asyncio.run(run())
print(f"AUDIO bytes received: {len(pcm)}")
if pcm:
    with wave.open("tts_sample.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(config.SIXTYDB_SAMPLE_RATE)
        w.writeframes(pcm)
    secs = len(pcm)/2/config.SIXTYDB_SAMPLE_RATE
    print(f"WROTE tts_sample.wav  (~{secs:.1f}s)  CHOSEN_VOICE_ID={vid}")
