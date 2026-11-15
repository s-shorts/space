# The Owl Files: episode toolkit

Episode 1 ("The Skeleton Lake") is the worked example. Copy this folder to a work directory and adapt it for each new episode.

## Setup
    pip install --break-system-packages kokoro-onnx soundfile skia-python
    mkdir -p tts tr
    curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    curl -sSL -o tts/voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## Order of work (run everything from the work directory)
1. `lines.py`: the script as `(scene number, on-screen caption text, spoken text or None)`. Spoken text spells numbers as words and names phonetically ("Ooloo" for Ullu). Scene 0 is the cold open, 1 the host intro, last scene the verdict and sign-off.
2. `python3 tts.py`: narration (80% hm_omega + 20% bm_george, en-gb, speed 0.93) -> `tts/l*.wav`, `tts/lines.json`. Aim for 4:10-4:50 total.
3. `python3 timeline.py`: line start times, scene starts, title-card time, `voice.wav`, `env.npy` (beak movement). The list of line indices that get an extra pause is episode-specific: update it.
4. `render.py`: everything above `# ================= SCENES` is the reusable engine (text, cards, stamps, crosses, skull, person, mountains, snowfall, board, owl host, captions, grain). Keep `s0` cold-open structure, `title`, `office`, `desk`, `s1` host intro and the end card in the last scene; rewrite the case-specific scenes with NEW visuals for the new case. Visual cues are keyed to line numbers with `cue(i)` / `cend(i)`, so every index must be updated to the new script. Change "CASE #001" and the title text.
   - `python3 render.py still 5 13 40 ...` writes test frames; `python3 sheet.py sheet.jpg` joins them. Look at frames from every scene before the full render. Captions sit at y 948-1026 and the corner host at the bottom right: keep cards clear of both.
   - `python3 render.py N` renders scene N to `scN.mp4`. Run two processes in parallel (even and odd scenes), about 10 minutes in total.
5. `python3 audio.py`: music bed + effects -> `mix.wav`. The effect cue lists are episode-specific: update the line indices.
6. Join: concat `sc*.mp4` with `-c copy`, then add `mix.wav` and re-encode with `-crf 27 -preset fast` (film grain makes lower CRF files huge). Must be under 95 MB.
7. Trailer Short (queue it with `--link-to <full video queue id>` and put `Watch the full video: {FULL_VIDEO_URL}` in its description; the poster fills in the link): the LAST spoken line is always exactly "The full video is available on our channel. Kindly visit to watch." and the end card says the same. `tr/tts.py` (max 5 short lines before that closing line, speed 1.06, total with pauses under 20 s), then `trailer.py` (set `SEG`: which scene and source time each line shows, and the crop centre x), `tr/cuts.json` = segment start times, `tr/audio.py`, mux, re-encode at CRF 27. 1080x1920.

`brand.py` drew the channel banner and profile picture.
