import numpy as np, soundfile as sf
sr=24000; v,_=sf.read("tr/voice.wav"); n=len(v); t=np.arange(n)/sr; T=n/sr; rng=np.random.default_rng(4)
def tone(f,d,dec,h=((1,1),(2,.4),(3,.2))):
    x=np.arange(int(d*sr))/sr; return sum(g*np.sin(2*np.pi*f*k*x) for k,g in h)*np.exp(-dec*x)*np.minimum(1,x*300)
def add(b,s,at,g):
    k=int(at*sr); m=min(len(s),n-k)
    if m>0: b[k:k+m]+=s[:m]*g
D=73.42; mus=np.zeros(n)
mus+=0.5*np.sin(2*np.pi*D*t)+0.25*np.sin(2*np.pi*D*1.5*t)+0.15*np.sin(2*np.pi*D*2*t+1)
mus*=np.clip(t/1.0,0,1)*(1+0.3*np.sin(2*np.pi*0.25*t))
# rising pulse (heartbeat)
bt=0.0
while bt<T-1:
    add(mus,tone(55,0.3,14,((1,1),(2,.3))),bt,1.4); add(mus,tone(55,0.25,16,((1,1),)),bt+0.22,0.9); bt+=0.9-0.35*(bt/T)
sc=[1,16/15,5/4,3/2,8/5]; p=0
for k,at in enumerate(np.arange(0.4,T-1.5,0.45)): add(mus,tone(D*4*sc[[0,2,3,1,4,3,2,1][k%8]],1.2,4,((1,1),(2,.5),(4.02,.15))),at,0.18)
env=np.convolve(np.abs(v),np.ones(6000)/6000,'same'); mus=mus/np.max(np.abs(mus))*(1-0.4*np.clip(env/0.08,0,1))
sfx=np.zeros(n)
def thud():
    x=np.arange(int(.4*sr))/sr; return np.sin(2*np.pi*(80*np.exp(-x*8)+40)*x)*np.exp(-x*10)
import json
for at in json.load(open("tr/cuts.json")): add(sfx,thud(),at,1.0); 
nz=rng.normal(0,1,n); nz=np.convolve(nz,np.ones(80)/80,'same'); nz/=np.max(np.abs(nz))
for at in json.load(open("tr/cuts.json")): 
    k=int((at-0.3)*sr); m=int(0.4*sr); 
    if k>0: sfx[k:k+m]+=nz[k:k+m]*np.sin(np.linspace(0,np.pi,m))**2*0.6
mix=v*0.95+mus*0.16+sfx*0.22; mix=np.tanh(mix*1.1); mix/=np.max(np.abs(mix))*1.06
sf.write("tr/mix.wav",np.stack([mix,mix],1),sr)
