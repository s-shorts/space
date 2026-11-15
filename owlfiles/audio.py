import numpy as np, soundfile as sf, json
TL=json.load(open("timeline.json")); LN=TL["lines"]; SC={int(k):v for k,v in TL["sc"].items()}; T=TL["total"]; sr=24000
v,_=sf.read("voice.wav"); n=len(v); t=np.arange(n)/sr; rng=np.random.default_rng(2)
cue=lambda i:LN[i]["s"]; cend=lambda i:LN[i]["e"]
def add(buf,sig,at,g=1.0):
    k=int(at*sr)
    if k>=n or k<0: return
    m=min(len(sig),n-k); buf[k:k+m]+=sig[:m]*g
def tone(f,d,dec=6.0,harm=((1,1),(2,.3),(3,.12))):
    x=np.arange(int(d*sr))/sr; return sum(g*np.sin(2*np.pi*f*h*x) for h,g in harm)*np.exp(-dec*x)*np.minimum(1,x*400)
# --- music: slow mysterious bed in D, Bhairav-ish scale (D Eb F# G A Bb C#)
D=146.83; sc=[1,16/15,5/4,4/3,3/2,8/5,15/8,2]
mus=np.zeros(n); beat=60/84
# drone
for f,g in ((D/2,.5),(D*3/4,.22),(D,.18)):
    mus+=g*np.sin(2*np.pi*f*t+rng.uniform(0,6))*(1+.2*np.sin(2*np.pi*.07*t+f))
mus*=0.5
# pluck pattern (santoor-like), varies every 8 beats
pat=[[0,4,7,4,2,4,1,0],[0,2,4,5,4,2,1,0],[7,5,4,2,4,5,4,2],[0,4,5,4,7,5,4,1]]
b=0; tt=SC[1]
while tt<T-3:
    p=pat[(b//8)%4][b%8]; f=D*sc[p]*(2 if (b//16)%2 else 1)
    add(mus,tone(f,1.6,3.5,((1,1),(2,.5),(3,.25),(4.02,.12))),tt,0.16 if b%2==0 else 0.10)
    if b%4==0: add(mus,tone(D/2,1.2,5,((1,1),(2,.4))),tt,0.35)          # bass pulse
    if b%2==1:                                                         # soft shaker
        nz=rng.normal(0,1,int(.06*sr))*np.exp(-np.arange(int(.06*sr))/sr*60); add(mus,nz,tt,0.03)
    tt+=beat/2 if False else beat; b+=1
# cold open: wind + low drone swell
w=rng.normal(0,1,n); W=400; w=np.convolve(w,np.ones(W)/W,'same'); w/=np.max(np.abs(w))
wind=w*(0.5+0.5*np.sin(2*np.pi*.18*t))*np.clip(1-(t-SC[1]+2)/2,0,1)*np.clip(t/1.5,0,1)
# duck music under voice
env=np.abs(v); k=int(.25*sr); env=np.convolve(env,np.ones(k)/k,'same'); duck=1-0.45*np.clip(env/0.08,0,1)
mus=mus/np.max(np.abs(mus))*duck
fade=np.clip(t/2,0,1)*np.clip((T-t)/3,0,1)
# --- sfx
sfx=np.zeros(n)
def whoosh(d=.5):
    x=np.arange(int(d*sr))/sr; z=rng.normal(0,1,len(x)); z=np.convolve(z,np.ones(60)/60,'same'); return z/np.max(np.abs(z))*np.sin(np.pi*x/d)**2
def thud():
    x=np.arange(int(.35*sr))/sr; return np.sin(2*np.pi*(90*np.exp(-x*9)+45)*x)*np.exp(-x*12)+rng.normal(0,1,len(x))*np.exp(-x*70)*.5
def popc(f=880): return tone(f,.18,22,((1,1),(2,.3)))
def ding(f=1320): return tone(f,.9,5,((1,1),(2.76,.3),(5.4,.1)))
for s in list(SC.values())[1:]: add(sfx,whoosh(),s-0.25,0.5)
add(sfx,whoosh(.8),TL["title"]-0.1,0.6); add(sfx,thud(),TL["title"]+0.55,1.0)
d=lambda i,fr:cue(i)+(cend(i)-cue(i))*fr
for at in [d(16,.72),cue(18)+.25,cue(18)+.53,cue(18)+.81,d(26,.78),cue(47)+.6,cue(48)+.7,d(53,.5)]: add(sfx,thud(),at,0.9)
add(sfx,thud(),cue(29)+0.5,1.2); add(sfx,whoosh(1.0),cue(29)+0.3,0.8)
for at in [cue(4)+.3,cue(6),d(6,.3),d(6,.55),cue(7),cue(10)-.1,cue(13),d(13,.4),cue(14),cue(15),d(17,.22),d(17,.5),d(17,.72),d(18,.55),cue(20)-.2,cue(20)+1,cue(21),d(21,.17),d(21,.36),cue(22)-.2,cue(23)-.2,cue(28)-.2,cue(30)+.6,cue(32)+.6,cue(35)+.5,cue(31)+.9,cue(34)+.8,cue(38)-.1,cue(39)-.1,cue(40)-.1,cue(43)-.1,cue(41)-.2,cue(42),d(42,.3),d(42,.55),d(42,.8),cue(44)-.1,cue(45)-.1,cue(47)-.1,cue(48)-.1,cue(50)-.1,cue(51)-.1]:
    add(sfx,popc(700+rng.integers(0,5)*90),at,0.35)
for at in [cue(8)+1.4,cue(9)+1.4,cue(36)+.4,cue(52)+.2]: add(sfx,ding(),at,0.25)
add(sfx,ding(660),cue(2)+0.6,0.3)
mix=v*0.95+mus*0.10*fade+wind*0.10+sfx*0.16
mix=np.tanh(mix*1.15); mix/=np.max(np.abs(mix))*1.06
sf.write("mix.wav",np.stack([mix,mix],1),sr); print(T,len(mix)/sr)
