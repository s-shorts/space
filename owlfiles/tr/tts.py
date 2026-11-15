import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k=Kokoro("tts/kokoro.onnx","tts/voices.bin")
v=0.8*k.get_voice_style("hm_omega")+0.2*k.get_voice_style("bm_george")
L=[("1942. A tiny frozen lake in the Himalayas.","Nineteen forty-two. A tiny frozen lake, in the Himalayas."),
   ("And inside it... hundreds of human skeletons.",None),
   ("A deadly hailstorm? Case closed.",None),
   ("Then the DNA came back.","Then the D N A came back."),
   ("They died 1,000 years apart. And some had Greek-like ancestry!","They died a thousand years apart. And some had Greek-like ancestry!"),
   ("Who were they?",None),
   ("The full video is available on our channel. Kindly visit to watch.",None)]
out=[]
for i,(d,s) in enumerate(L):
    a,sr=k.create(s or d,voice=v,speed=1.06,lang="en-gb")
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-500):idx[-1]+1800]
    sf.write(f"tr/l{i}.wav",a,sr); out.append(dict(t=d,d=len(a)/sr))
json.dump(out,open("tr/lines.json","w"),indent=1); print([round(o["d"],2) for o in out], round(sum(o["d"] for o in out),2))
