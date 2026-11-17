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


## VISUAL STANDARD (from 18 Nov 2026): animated-film look, always
Viewer feedback on Raat Files #001 (flat code-drawn "case dossier" icons): visuals were not
good enough. Every episode of BOTH series must now look like a stylized 3D animated feature
film, moving the whole time. Flat vector icons/cards/stamps are no longer a style of their
own -- at most small overlays (a date, a "CAUGHT" stamp, a label) on top of cinematic shots.

How (see `cine.py` and the 10 s reference test it was built with):
1. PLATES: 12-18 AI-generated stills per episode through the assets-request fetcher, every
   prompt starting with the same episode style string, e.g. "stylized 3D animated feature
   film background, no characters, cinematic composition, volumetric fog and moonlight,
   soft global illumination, <grade> color grade, highly detailed" + the scene. Request
   width 1088, height 2048 (portrait). One shot per beat: establishing exterior, rooms,
   objects, close-ups of the key evidence, a period/place detail. Use seeds per episode.
   Free mode returns ~560x1050 with a "pollinations.ai" strip at the bottom and often a few
   503 errors: request ~20% extra, re-request failures once, `cine.Plate` crops the strip and
   upscales. No characters/people inside plates (the free model can't keep them consistent);
   never depict real victims' faces.
2. HOSTS: use the fixed host art -- `owlfiles/host_art/owl_idle.jpg` (Professor Ullu) and
   `raatfiles/host_art/bat_idle.jpg`, `bat_scared.jpg` (Inspector Raat) -- as cinematic host
   shots (push-in, lamp/moon grade, dust, flicker) for the intro, verdict and end card. They
   are the canonical look now, so the hosts are identical in every episode. The old
   code-drawn `owl()`/`bat()` may still appear only as a tiny corner cameo, or not at all.
3. MOTION: every shot is a `cine.Shot` with a camera move (push / pull / pans / tilts /
   drift), parallax fog, particles (dust, embers, rain via dust_col), light flicker or
   shafts, lightning where it fits, and a grade. Shots 2.5-5 s, cut on the voice; mix cuts:
   whip-pan (`whip`), crossfade, hard cut on a sound hit. Nothing static longer than ~1.5 s.
   Overlays (dates, names, "AI reconstruction" label, stamps) animate in with ease/scale.
   Finish every frame with `film_finish` (grain + vignette) after captions.
4. CAPTIONS: big, bold, cinematic subtitles (1-2 lines, wrap at ~W-160 px, stroke outline),
   bottom third around y=1480, never over the subject's face.
5. SOUND: under the music add room tone, wind/rain, creaks, a whoosh on every whip-pan,
   a low boom on reveals and a riser before the verdict.
6. LABEL: small "AI reconstruction" tag on AI shots; set "ai_disclosure": true in the
   queue JSON whenever AI plates are used (they always are now).
7. If the repo secret POLLINATIONS_API_KEY is set (assets manifest "has_key": true), also
   request 3-6 AI video clips (`kind: video`, image-to-video from your best plates, 5 s)
   for the key moments, and ask for higher-resolution plates with the best image model the
   manifest lists. Without a key, plates + cine.py motion are the standard.
8. QA: contact sheet of 8-12 frames before the full render; reject any plate with
   distorted anatomy, text gibberish, a human face, or a clashing style, and regenerate.

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
