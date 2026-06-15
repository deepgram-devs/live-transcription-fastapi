import json, urllib.request, config
req = urllib.request.Request("https://api.60db.ai/voices",
    headers={"Authorization": f"Bearer {config.SIXTYDB_API_KEY}"})
with urllib.request.urlopen(req, timeout=20) as r:
    body = json.loads(r.read().decode())
data = body["data"]
print("type(data):", type(data).__name__)
if isinstance(data, dict):
    print("data keys:", list(data.keys()))
    for k, v in data.items():
        print(f"  {k}: {type(v).__name__}" + (f" len={len(v)}" if isinstance(v,(list,dict)) else f" = {v!r}"))
        if isinstance(v, list) and v and isinstance(v[0], dict):
            print("   first item keys:", list(v[0].keys()))
            print("   first item:", json.dumps(v[0])[:400])
