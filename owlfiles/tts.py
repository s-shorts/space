import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from lines import L
k=Kokoro("tts/kokoro.onnx","tts/voices.bin")
v=0.8*k.get_voice_style("hm_omega")+0.2*k.get_voice_style("bm_george")
out=[]
for i,(sc,d,s) in enumerate(L):
    a,sr=k.create(s or d,voice=v,speed=0.93,lang="en-gb")
    # trim silence
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-600):idx[-1]+2400]
    sf.write(f"tts/l{i}.wav",a,sr); out.append(dict(sc=sc,t=d,d=len(a)/sr))
json.dump(out,open("tts/lines.json","w"),indent=1)
print(sum(o["d"] for o in out), len(out), sum(len(x[1].split()) for x in L))
