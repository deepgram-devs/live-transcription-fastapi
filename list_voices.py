import json, urllib.request, config

req = urllib.request.Request(
    "https://api.60db.ai/voices",
    headers={"Authorization": f"Bearer {config.SIXTYDB_API_KEY}"},
)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:300]); raise SystemExit
except Exception as e:
    print("ERROR", type(e).__name__, e); raise SystemExit

# Find the list of voices regardless of envelope shape
data = body.get("data", body) if isinstance(body, dict) else body
voices = data.get("voices", data) if isinstance(data, dict) else data
print("top-level keys:", list(body.keys()) if isinstance(body, dict) else type(body))
print("voice count:", len(voices) if isinstance(voices, list) else "n/a")
for v in (voices[:8] if isinstance(voices, list) else []):
    vid = v.get("voice_id") or v.get("id") or v.get("voiceId")
    print(f"  id={vid!r:40}  name={v.get('name')!r}  lang={v.get('language') or v.get('lang')!r}")
