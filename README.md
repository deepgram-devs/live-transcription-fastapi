# Live Transcription With Python and FastAPI

To run this project create a virtual environment by running the below commands. You can learn more about setting up a virtual environment in this [article](https://developers.deepgram.com/blog/2022/02/python-virtual-environments/). 

```
mkdir [% NAME_OF_YOUR_DIRECTORY %]
cd [% NAME_OF_YOUR_DIRECTORY %]
python3 -m venv venv
source venv/bin/activate
```

Make sure your virtual environment is activated and install the dependencies in the requirements.txt file inside. 

```
pip install -r requirements.txt
```

Make sure you're in the directory with the **main.py** file and run the project in the development server.

```
uvicorn main:app --reload
```

Pull up a browser and go to your localhost, http://127.0.0.1:8000/.

Allow access to your microphone and start speaking. A transcript of your audio will appear in the browser. 

## Configuration

Copy `.env.example` to `.env` and fill in your keys:

```
DEEPGRAM_API_KEY=...   # speech-to-text
SIXTYDB_API_KEY=...    # text-to-speech (60db)
```

See `.env.example` for the optional 60db voice/encoding overrides.

## Text-to-speech with 60db

This project also integrates **60db** as a text-to-speech provider alongside
Deepgram's speech-to-text. On the same page, type text into the "Speak Text"
box and click **Speak** — the audio is synthesized by 60db and played back in
the browser.

### Architecture

Both voice services sit behind a small provider abstraction so the app does not
depend on any single vendor:

| Layer | File | Role |
|-------|------|------|
| Interfaces | `providers/base.py` | `STTProvider` / `STTSession` (push audio in, get transcripts) and `TTSProvider` (text in, audio frames out) |
| STT adapter | `providers/deepgram_stt.py` | Wraps the Deepgram live socket |
| TTS adapter | `providers/sixtydb_tts.py` | 60db WebSocket protocol (`create_context` → `send_text` → `flush` → `audio_chunk` frames) |
| Config | `config.py` | All env vars / tunables in one place |
| App | `main.py` | `/listen` WebSocket (STT) and `/speak` WebSocket (TTS), wired to the providers |

Because both adapters implement the shared interfaces, swapping in another STT
or TTS vendor only means adding a new adapter and changing the wiring in
`main.py` — the endpoints and the rest of the app stay the same.

