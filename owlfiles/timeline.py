import json, numpy as np, soundfile as sf
L=json.load(open("tts/lines.json")); sr=24000; FPS=30
t=0.9; TITLE=3.4; out=[]; sc_start={0:0.0}
for i,l in enumerate(L):
    if i and l["sc"]!=L[i-1]["sc"]:
        if L[i-1]["sc"]==0: t+=0.5; title_at=t; t+=TITLE
        t+=0.7; sc_start[l["sc"]]=round((t-0.45)*FPS)/FPS
    out.append(dict(i=i,sc=l["sc"],t=l["t"],s=t,e=t+l["d"])); t+=l["d"]+0.42
    if i in (2,4,16,18,26,27,29,36,43,48,51): t+=0.45
total=round((t+4.2)*FPS)/FPS
n=int(total*sr)+1; v=np.zeros(n)
for o in out:
    a,_=sf.read(f"tts/l{o['i']}.wav"); k=int(o["s"]*sr); v[k:k+len(a)]+=a
v/=np.max(np.abs(v)); sf.write("voice.wav",v,sr)
nf=int(total*FPS); hop=sr//FPS
env=np.array([np.sqrt(np.mean(v[f*hop:(f+1)*hop]**2)) for f in range(nf)])
env=np.clip(env/np.percentile(env[env>0.01],85),0,1); np.save("env.npy",env)
json.dump(dict(lines=out,sc=sc_start,title=title_at,total=total,TITLE=TITLE),open("timeline.json","w"),indent=1)
print(total, sc_start, title_at)
