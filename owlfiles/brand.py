import skia, numpy as np, math, random
from PIL import Image
exec(open("render.py").read().split("# ================= SCENES")[0].replace('TL = json.load(open("timeline.json"))','TL = json.load(open("timeline.json"))'))
def surface(w,h):
    arr=np.zeros((h,w,4),np.uint8); s=skia.Surface(arr); return arr,s,s.getCanvas()
def owl_static(c,x,y,s,look=(0.15,0),brow=0.25,prop="glass",wing=0.0):
    owl(c,x,y,s,0.6,0,look=look,brow=brow,prop=prop,talk=0.0,wing=wing)

# ---------- PROFILE 800x800
arr,su,c=surface(800,800)
grad_rect(c,0,0,800,800,"#1b3f4a","#0d2029")
p=skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial((400,330),520,[col("#ffe9b0",0.28),col("#ffe9b0",0)])); c.drawRect(skia.Rect.MakeWH(800,800),p)
c.drawCircle(400,400,372,P(MUST,0.9,stroke=10))
owl_static(c,400,955,1.24,look=(0.05,0.05),brow=0.3,prop=None)
su.flushAndSubmit(); Image.fromarray(arr[...,:3]).save("owlfiles_profile_800.png")

# ---------- BANNER 2560x1440
W2,H2=2560,1440
arr,su,c=surface(W2,H2)
grad_rect(c,0,0,W2,H2,"#173640","#0d2029")
for k in range(0,W2,96): c.drawLine(k,0,k,H2,P("#ffffff",0.02,stroke=2))
# cork board across safe band
bx,by,bw,bh=380,515,1800,410
rrect(c,bx+14,by+18,bw,bh,16,P("#000000",0.4,blur=20)); rrect(c,bx,by,bw,bh,16,P("#5a3b25")); rrect(c,bx+22,by+22,bw-44,bh-44,8,P(CORK))
r=random.Random(5)
for k in range(900): c.drawCircle(bx+22+r.random()*(bw-44),by+22+r.random()*(bh-44),1+r.random()*2.5,P("#8f6238",0.5))
pl=skia.Paint(AntiAlias=True); pl.setShader(skia.GradientShader.MakeRadial((1280,420),1300,[col("#ffe9b0",0.18),col("#ffe9b0",0)])); c.drawRect(skia.Rect.MakeWH(W2,H2),pl)
# pinned items (outer, may be cropped on mobile)
def pinned(x,y,w,h,rot,colr=PAPER,pin=RED):
    c.save(); c.translate(x+w/2,y+h/2); c.rotate(rot); c.translate(-w/2,-h/2)
    rrect(c,8,12,w,h,6,P("#000000",0.3,blur=10)); rrect(c,0,0,w,h,6,P(colr))
    c.drawCircle(w/2,16,13,P(pin)); c.drawCircle(w/2-4,12,4,P("#ffffff",0.6))
pinned(560,575,220,260,-5); skull(c,110,150,1.15,1,"#e9dcc0",crack=1); c.restore()
pinned(1790,580,230,170,4,MUST,INK); text(c,"No proof,",115,82,36,"b",INK,anchor="c"); text(c,"no chai.",115,130,36,"b","#7a2313",anchor="c"); c.restore()
c.drawLine(780,690,830,690,P(RED,0.9,stroke=5)); c.drawLine(1730,690,1790,660,P(RED,0.9,stroke=5))
# title card centre (safe area 1546x423 centred: x 507-2053, y 508-931)
c.save(); c.translate(1280,720); c.rotate(-2)
rrect(c,-440,-180,880,360,14,P("#000000",0.4,blur=16)); rrect(c,-440,-180,880,360,14,P("#d9ab5c")); rrect(c,-414,-156,828,312,8,P(PAPER))
text(c,"CASE FILES  ·  EVIDENCE ONLY",0,-104,28,"t","#6b5a3c",anchor="c")
c.drawLine(-370,-84,370,-84,P("#6b5a3c",0.4,stroke=3))
text(c,"THE OWL",0,6,110,"b",INK,anchor="c"); text(c,"FILES",0,108,110,"b",RED,anchor="c")
c.restore()
# tagline under board
text(c,"Real mysteries.",290,700,44,"s",PAPER,0.95,"c"); text(c,"Real evidence.",290,760,44,"s",PAPER,0.95,"c"); text(c,"Case still open.",290,820,44,"s",MUST,1,"c")
# stamp
c.save(); c.translate(1600,870); c.rotate(-12); font=skia.Font(TF["b"],52); s="UNSOLVED"; w=font.measureText(s)
rrect(c,-w/2-26,-50,w+52,80,10,P(PAPER,0.9)); rrect(c,-w/2-26,-50,w+52,80,10,P(RED,stroke=7)); c.drawString(s,-w/2,8,font,P(RED)); c.restore()
# owl on right edge (desktop-visible)
owl_static(c,2290,935,0.66,look=(-0.7,-0.2),brow=0.4,prop="glass")
# snow/stars left edge
for k in range(120): c.drawCircle(r.random()*360,r.random()*H2,1+2*r.random(),P("#ffffff",0.2+0.4*r.random()))
# grain + vignette
g=np.random.default_rng(1).integers(0,255,(H2//2,W2//2),dtype=np.uint8); a=np.zeros((H2//2,W2//2,4),np.uint8); a[...,0]=a[...,1]=a[...,2]=g; a[...,3]=14
c.drawImageRect(skia.Image.fromarray(a),skia.Rect.MakeWH(W2,H2))
su.flushAndSubmit(); Image.fromarray(arr[...,:3]).save("owlfiles_banner_2560x1440.png")
# safe-area preview
im=Image.open("owlfiles_banner_2560x1440.png").convert("RGB")
from PIL import ImageDraw
pv=im.copy(); d=ImageDraw.Draw(pv); d.rectangle([507,508,2053,931],outline=(0,255,0),width=6); d.rectangle([0,508,2559,931],outline=(255,255,0),width=4)
pv.resize((1280,720)).save("banner_preview.jpg",quality=85)
Image.open("owlfiles_profile_800.png").resize((400,400)).save("profile_preview.jpg")
