# The Owl Files: episode toolkit

Episode 1 ("The Skeleton Lake") is the worked example — it was made and published as a
4-5 min 1920x1080 video plus a separate 20 s 1080x1920 trailer Short. That split is
retired as of 17 Nov 2026: every episode from here on is ONE standalone vertical Short,
1080x1920, 2:30-3:00 (never over 3:00 — YouTube caps Shorts there), posted directly with
no separate "full video" and no trailer. Copy this folder to a work directory and adapt
it for each new episode; treat episode 1's `render.py` as a reference for pacing and
jokes only — its scene pixel-coordinates are landscape and must be redrawn for the
1080-wide portrait canvas (the engine defaults — canvas size, caption position, corner
host position — are already updated to portrait at the top of `render.py`).

For the sister segment "Raat Files" (true paranormal/horror incidents, hosted by
Inspector Raat the bat), see `../raatfiles/README.md` — it reuses this same toolkit and
engine, swapping in its own host and palette.

## Setup
    pip install --break-system-packages kokoro-onnx soundfile skia-python
    mkdir -p tts
    curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    curl -sSL -o tts/voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## Order of work (run everything from the work directory)
1. `lines.py`: the script as `(scene number, on-screen caption text, spoken text or None)`. Spoken text spells numbers as words and names phonetically ("Ooloo" for Ullu). Scene 0 is the cold open, 1 the host intro, last scene the verdict, comment question and sign-off. About 28-34 lines, 300-360 words total — roughly half of episode 1's script, since the whole episode is now the Short. Keep the cold open getting straight to the hook, and the host intro to just 1-2 short lines (one joke, name the case) — most of the runtime should go to the case itself, not the greeting.
2. `python3 tts.py`: narration (80% hm_omega + 20% bm_george, en-gb, speed 0.93) -> `tts/l*.wav`, `tts/lines.json`. Aim for 2:30-2:55 of narration, leaving room for the cold open and end card beats so the final render lands under 3:00.
3. `python3 timeline.py`: line start times, scene starts, title-card time, `voice.wav`, `env.npy` (beak movement). The list of line indices that get an extra pause is episode-specific: update it.
4. `render.py`: everything above `# ================= SCENES` is the reusable engine (text, cards, stamps, crosses, skull, person, mountains, snowfall, board, owl host, captions, grain) — already set up for the 1080x1920 canvas. Keep the cold-open structure, title card, host intro and an end card in the last scene; rewrite the case-specific scenes with NEW visuals for the new case, laid out for portrait. Visual cues are keyed to line numbers with `cue(i)` / `cend(i)`, so every index must match the new script. Change "CASE #001" and the title text. The end card now IS the only call-to-action (there's no separate trailer to point to): have it say plainly that this is the episode, invite a comment, and sign off — no "watch the full video" line, since this already is the full thing.
   - `python3 render.py still 5 13 40 ...` writes test frames; `python3 sheet.py sheet.jpg` joins them. Look at frames from every scene before the full render. Captions sit centered around y 1500-1560 and the corner host near the bottom-right (x~970, y~1840): keep cards clear of both, and keep key content out of the top ~180px and bottom ~280px (Shorts UI safe zone).
   - `python3 render.py N` renders scene N to `scN.mp4`. Run two processes in parallel (even and odd scenes).
5. `python3 audio.py`: music bed + effects -> `mix.wav`. The effect cue lists are episode-specific: update the line indices.
6. Join: concat `sc*.mp4` with `-c copy`, then add `mix.wav` and re-encode with `-crf 27 -preset fast` (film grain makes lower CRF files huge). Must be under 95 MB (a ~3 min Short at this bitrate is normally well under that).

`brand.py` drew the channel banner and profile picture.
