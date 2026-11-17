# Raat Files: the paranormal-incidents segment

A second daily Short on The Owl Files (@TheOwlFiles), alongside the Owl Files case
(Professor Ullu). Same channel, same production engine, different host and tone:
real, documented reports of paranormal and horror incidents, told with the same
evidence-honest spirit as Owl Files -- never asserting a haunting is proven real.
Added 17 Nov 2026.

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

## Visual style
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
