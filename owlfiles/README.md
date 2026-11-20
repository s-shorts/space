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


## LANGUAGE: HINDI (from 21 Nov 2026) -- applies to Owl Files AND Raat Files
Both series are now made in Hindi (everyday spoken Hindi, Hindustani register -- simple,
conversational, the way a YouTuber talks; common English words like "case", "evidence",
"DNA", "theory" are fine, written in Devanagari).
- SCRIPT IN DEVANAGARI ONLY. Kokoro's Hindi voices read Devanagari correctly; romanized
  Hindi ("Main Raat hoon") gets English pronunciation and sounds wrong. Write English
  loanwords and names in Devanagari too: इंस्पेक्टर, एविडेंस, एनफ़ील्ड, नासा. Numbers
  spoken as Hindi words in the spoken text (उन्नीस सौ सतहत्तर), digits on screen (1977).
- VOICES (Kokoro, lang="hi", no English-voice blend any more):
    Professor Ullu  -> hm_omega, speed 0.95
    Inspector Raat  -> hm_psi,   speed 0.90 (a touch slower, nervous night-time feel)
  In tts.py: `k.create(text, voice="hm_omega", speed=0.95, lang="hi")`. Read the sample
  output aloud-length check: Hindi runs a little slower than English, so 2:30-2:55 of
  narration is about 280-330 Hindi words.
- ON-SCREEN TEXT: skia does NOT shape Devanagari (matras/conjuncts break: किला -> कलि).
  Draw ALL Hindi text (captions, titles, cards, stamps, end card) with `hindi_text.py`
  (hi_text / hi_lines / hi_caption -- Poppins via Pillow+raqm), never c.drawString.
  Short English labels (DNA, 1977, "CASE #003") may still use the old skia text code.
  Check every Hindi word in the contact sheet for broken matras before the full render.
- NAMES: "प्रोफ़ेसर उल्लू" / "इंस्पेक्टर रात"; title cards "द आउल फ़ाइल्स · केस #00N" and
  "रात फ़ाइल्स · केस #00N".
- CATCHPHRASES IN HINDI: Ullu -- "नो प्रूफ़, नो चाय", sign-off "जिज्ञासु रहिए, और किसी फ़ॉरवर्ड
  पर भरोसा मत कीजिए।" then "केस... अभी खुला है।"  Raat -- "नो रिकॉर्ड, नो रेस्ट", "मैं यहाँ सिर्फ़
  कागज़ी कार्रवाई के लिए हूँ", sign-off "जिज्ञासु रहिए। और एक आँख खोलकर सोइए।"
- YOUTUBE TEXT: title in Hindi (Devanagari) with the place/case name also in English so
  both searches find it, under 70 chars, ending #shorts -- e.g.
  "भानगढ़ किला: सूरज ढलने के बाद एंट्री बैन क्यों? | Bhangarh Fort #shorts".
  Description in Hindi, sources as plain "Name: URL" lines, then the series line in
  Hindi + the AI-tools line in Hindi, then 3-4 hashtags (#shorts plus Hindi/English tags).
  Tags: mix Hindi and English search terms.

## TOPIC ORDER: Indian and global, one by one (from 21 Nov 2026)
Each series alternates its OWN episodes strictly: Indian case, then global case, then
Indian, then global... Look at that series' last episode in its episode-log.md: if it was
Indian, this one is global, and vice versa. (Owl Files and Raat Files alternate
independently.) The category rotation still applies within that constraint.

## Setup
    pip install --break-system-packages kokoro-onnx soundfile skia-python
    mkdir -p tts
    curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    curl -sSL -o tts/voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## Order of work (run everything from the work directory)
1. `lines.py`: the script as `(scene number, on-screen caption text, spoken text or None)`. Spoken text spells numbers as words, all in Devanagari (see LANGUAGE: HINDI). Scene 0 is the cold open, 1 the host intro, last scene the verdict, comment question and sign-off. About 28-34 lines, 300-360 words total — roughly half of episode 1's script, since the whole episode is now the Short. Keep the cold open getting straight to the hook, and the host intro to just 1-2 short lines (one joke, name the case) — most of the runtime should go to the case itself, not the greeting.
2. `python3 tts.py`: narration (HINDI since 21 Nov 2026: hm_omega, lang hi, speed 0.95 -- see LANGUAGE: HINDI above; episode 1 used 80% hm_omega + 20% bm_george, en-gb) -> `tts/l*.wav`, `tts/lines.json`. Aim for 2:30-2:55 of narration, leaving room for the cold open and end card beats so the final render lands under 3:00.
3. `python3 timeline.py`: line start times, scene starts, title-card time, `voice.wav`, `env.npy` (beak movement). The list of line indices that get an extra pause is episode-specific: update it.
4. `render.py`: everything above `# ================= SCENES` is the reusable engine (text, cards, stamps, crosses, skull, person, mountains, snowfall, board, owl host, captions, grain) — already set up for the 1080x1920 canvas. Keep the cold-open structure, title card, host intro and an end card in the last scene; rewrite the case-specific scenes with NEW visuals for the new case, laid out for portrait. Visual cues are keyed to line numbers with `cue(i)` / `cend(i)`, so every index must match the new script. Change "CASE #001" and the title text. The end card now IS the only call-to-action (there's no separate trailer to point to): have it say plainly that this is the episode, invite a comment, and sign off — no "watch the full video" line, since this already is the full thing.
   - `python3 render.py still 5 13 40 ...` writes test frames; `python3 sheet.py sheet.jpg` joins them. Look at frames from every scene before the full render. Captions sit centered around y 1500-1560 and the corner host near the bottom-right (x~970, y~1840): keep cards clear of both, and keep key content out of the top ~180px and bottom ~280px (Shorts UI safe zone).
   - `python3 render.py N` renders scene N to `scN.mp4`. Run two processes in parallel (even and odd scenes).
5. `python3 audio.py`: music bed + effects -> `mix.wav`. The effect cue lists are episode-specific: update the line indices.
6. Join: concat `sc*.mp4` with `-c copy`, then add `mix.wav` and re-encode with `-crf 27 -preset fast` (film grain makes lower CRF files huge). Must be under 95 MB (a ~3 min Short at this bitrate is normally well under that).

`brand.py` drew the channel banner and profile picture.
