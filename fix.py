import asyncio, json, os, edge_tts
L = json.load(open("lines.json")); os.makedirs("out", exist_ok=True)
async def synth(text, path):
    c = edge_tts.Communicate(text, "en-IN-PrabhatNeural", rate="-6%", pitch="-2Hz", boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append([ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"], "W"])
    return words
async def main():
    meta = {}
    for k, t in L.items():
        for a in range(5):
            try: meta[k] = dict(text=t, words=await synth(t, f"out/{k}.mp3")); break
            except Exception as e: print("err", k, repr(e)); await asyncio.sleep(8)
    json.dump(meta, open("out/words.json", "w"))
asyncio.run(main())
