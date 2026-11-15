"""Comparison samples from AI4Bharat Indic Parler-TTS (open licence), Indian-English speakers."""
import json, os, torch, soundfile as sf
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
os.makedirs("out/samples", exist_ok=True)
S = json.load(open("script.json")); text = S["scenes"][0]["paras"][1]
M = "ai4bharat/indic-parler-tts"
model = ParlerTTSForConditionalGeneration.from_pretrained(M)
tok = AutoTokenizer.from_pretrained(M); dtok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
for spk in ["Thoma", "Mary", "Dinesh", "Raghav"]:
    desc = (f"{spk} speaks in a calm, slow, deep and soothing voice with an Indian English accent, like a documentary narrator. "
            "The recording is of very high quality, with the speaker's voice sounding clear and very close up.")
    try:
        torch.manual_seed(7)
        d = dtok(desc, return_tensors="pt"); p = tok(text, return_tensors="pt")
        a = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask, prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
        sf.write(f"out/samples/parler_{spk}.wav", a.cpu().numpy().squeeze(), model.config.sampling_rate); print("ok", spk, flush=True)
    except Exception as e:
        print("fail", spk, e, flush=True)
