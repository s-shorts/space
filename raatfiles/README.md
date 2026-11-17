# Raat Files: the paranormal-incidents segment

A second daily Short on The Owl Files (@TheOwlFiles), alongside the Owl Files case
(Professor Ullu). Same channel, same production engine, different host and tone:
real, documented reports of paranormal and horror incidents, told with the same
evidence-honest spirit as Owl Files -- never asserting a haunting is proven real.
Added 17 Nov 2026.


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

## Host: Inspector Raat
A fruit-bat detective, nocturnal counterpart to Professor Ullu. Round spectacles
(one lens comically cracked), a dark hooded cloak, a lantern (or an old case
notebook) instead of a magnifying glass or chai cup. Voice: Kokoro TTS blended
60% hm_omega + 40% bm_george (a slightly different mix from Owl Files' 80/20, so
the two hosts are recognisably different voices), en-gb, speed 0.95, same
Indian-accented-English target. Tagline: "Unexplained. Not unreal." Sign-off:
"Stay curious. Sleep with one eye open." Running jokes: he's a bat who's
afraid of the dark; "no proof, no chai" (Ullu's line) becomes his own
"no record, no rest"; he keeps insisting he's "purely here for the paperwork."
`host.py` in this folder has the character's draw code and palette -- paste it
into a copy of `../owlfiles/render.py` in place of `owl()`.

## The rule that matters most
Inspector Raat is still a detective, not a believer. Every episode presents a REAL,
documented incident -- a famous haunting, a historical case file, an investigated
sighting, a studied phenomenon -- states plainly what was reported, what (if
anything) was officially investigated or recorded, and what remains unexplained.
Never claims a ghost, curse or spirit is proven real; never invents a "true story"
with no real source. Debunked cases are fair game (and should say so plainly,
same as Owl Files' category H). This keeps the segment inside the channel's
existing evidence-based identity instead of becoming generic ghost-story content.

## Categories (rotate, same idea as Owl Files' topic rotation)
1. Documented hauntings: places with a real investigated history (forts, hotels, hospitals, ships, theatres).
2. Historic poltergeist/haunting case files studied by researchers, media or official bodies (e.g. Enfield).
3. Unexplained recordings and photographs: EVP, "ghost photos" -- what's known, what debunks or doesn't.
4. Mass sightings and shared panics: real historical events with many witnesses (phantom-image panics, shared hallucination events).
5. Cursed-object legends with real, traceable provenance (a museum piece, a famous "cursed" item with a documented ownership history).
6. Near-death / out-of-body experience research: the science and reported experience, no medical claims, no afterlife assertions.
7. Indian/Asian local legends with real documented history (Bhangarh Fort, Dow Hill, or similar -- verify primary sources, not just blogs).
8. Debunked "true" hauntings: infrasound, carbon monoxide, hoaxes, pareidolia -- the evidence gives a mundane answer; say so plainly.
At least one episode in three should be an Indian or Asian case, same as Owl Files.
Never: real recent deaths/tragedies for shock value, implying a real living person
is cursed or haunted, graphic descriptions, or presenting any paranormal claim as
confirmed fact.

## Visual style (palette/mood; the animated-film standard above always applies)
Night palette (deep indigo, moonlight silver, lantern-orange, used sparingly blood-red),
candlelight/flashlight-cone lighting, fog, grain -- same rotation idea as Owl Files
(case-board, photo-documentary with real archive photos, realistic render, map room,
blueprint, AI-cinematic reconstruction) but always kept moody/dark rather than bright.
Palette and the host's draw code are in `host.py`.

## Build
Same toolkit and order of work as `../owlfiles/README.md` (lines.py -> tts.py ->
timeline.py -> render.py -> audio.py), 1080x1920, 2:30-3:00, under 3:00 hard limit.
Copy `../owlfiles/` as the starting point, then:
1. Drop in this folder's `host.py` in place of `owl()` and the Owl Files palette line.
2. Replace every `owl(...)` / `host_corner(...)` call in the copied scenes with
   `bat(...)` / `host_corner_raat(...)`.
3. Write new case-specific scenes (cork board and stamps are optional here --
   evidence folders, case photographs, a flashlight-cone reveal, a cracked
   photograph, etc. fit the tone better, but reuse them if a case calls for it).
4. Title card: "RAAT FILES · CASE #00N" (its own numbering, separate from Owl Files'
   case numbers). End card: case verdict/status, a comment question, the sign-off,
   @TheOwlFiles -- no "watch the full video" line, this already is the whole Short.
