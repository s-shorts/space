# Raat Files: the paranormal-incidents segment

A second daily Short on The Owl Files (@TheOwlFiles), alongside the Owl Files case
(Professor Ullu). Same channel, same production engine, different host and tone:
real, documented reports of paranormal and horror incidents, told with the same
evidence-honest spirit as Owl Files -- never asserting a haunting is proven real.
Added 17 Nov 2026.



## NO HOST INTRO (from 21 Nov 2026)
Do not introduce Ullu or Raat at all -- no "मैं हूँ प्रोफ़ेसर उल्लू" / "मैं इंस्पेक्टर रात हूँ" line,
no greeting. The Short starts straight on the case: first spoken line is the hook, then a
1-2 second title card, then the case. The host still narrates and appears on screen
(corner host / reactions), a running joke may slip in mid-story where it fits, and the
end card keeps the comment question and the sign-off.

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

## Host: Inspector Raat
A fruit-bat detective, nocturnal counterpart to Professor Ullu. Round spectacles
(one lens comically cracked), a dark hooded cloak, a lantern (or an old case
notebook) instead of a magnifying glass or chai cup. Voice (Hindi since 21 Nov 2026): Kokoro hm_psi, lang hi,
speed 0.90 -- a different voice from Ullu's hm_omega (see LANGUAGE: HINDI). Episode 1
(English) used 60% hm_omega + 40% bm_george, en-gb. Tagline: "Unexplained. Not unreal." Sign-off:
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
