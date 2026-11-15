"""Narration with Microsoft neural Indian-English voices (edge-tts). One mp3 + word timings per paragraph."""
import asyncio, json, os, sys
import edge_tts

S = json.load(open("script.json"))
VOICE = S.get("voice", "en-IN-PrabhatNeural")
RATE, PITCH = os.environ.get("RATE", "-6%"), os.environ.get("PITCH", "-2Hz")
os.makedirs("out/tts", exist_ok=True)

async def synth(text, voice, path, rate=RATE, pitch=PITCH):
    try:
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    except TypeError:
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                words.append([ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"], ch["type"][0]])
    return words

async def main():
    meta = {}
    for sc in S["scenes"]:
        for i, p in enumerate(sc["paras"]):
            key = f"{sc['id']}_{i}"
            for attempt in range(4):
                try:
                    meta[key] = dict(text=p, words=await synth(p, VOICE, f"out/tts/{key}.mp3")); break
                except Exception as e:
                    print("retry", key, e); await asyncio.sleep(5)
            print(key, len(meta.get(key, {}).get("words", [])), flush=True)
    json.dump(meta, open("out/tts/words.json", "w"), indent=0)
    # voice comparison samples
    os.makedirs("out/samples", exist_ok=True)
    sample = S["scenes"][0]["paras"][1]
    for v in ["en-IN-PrabhatNeural", "en-IN-NeerjaNeural", "en-IN-NeerjaExpressiveNeural"]:
        try: await synth(sample, v, f"out/samples/edge_{v}.mp3")
        except Exception as e: print("sample fail", v, e)
    try:
        vs = await edge_tts.list_voices()
        json.dump([v for v in vs if v["Locale"].startswith("en-IN")], open("out/samples/en_IN_voices.json", "w"), indent=1)
    except Exception as e: print("list fail", e)

asyncio.run(main())
