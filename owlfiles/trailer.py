import json, sys, os, subprocess, math, numpy as np, soundfile as sf, skia
import render as R
from render import P, col, text, rrect, prog, pop, eout, ease, clamp, stamp, owl, MUST, RED, PAPER, INK, TEAL, TF
R.host_corner = lambda *a, **k: None
VW, VH, FPS = 1080, 1920, 30
L = json.load(open("tr/lines.json")); sr = 24000
LEAD, GAP, TAIL = 0.3, 0.12, 0.75
t = LEAD; TL = []
for i, l in enumerate(L):
    TL.append((t, t + l["d"], l["t"])); t += l["d"] + GAP + (0.12 if i in (1, 3) else 0)
TOTAL = round((TL[-1][1] + TAIL) * FPS) / FPS
# voice + env
n = int(TOTAL * sr) + 1; v = np.zeros(n)
for i, (s, e, _) in enumerate(TL):
    a, _ = sf.read(f"tr/l{i}.wav"); k = int(s * sr); v[k:k + len(a)] += a[:n - k]
v /= np.max(np.abs(v)); sf.write("tr/voice.wav", v, sr)
hop = sr // FPS; nf = int(TOTAL * FPS)
env = np.array([np.sqrt(np.mean(v[f * hop:(f + 1) * hop] ** 2)) for f in range(nf)]); env = np.clip(env / np.percentile(env[env > 0.01], 85), 0, 1)
cue = R.cue; cend = R.cend
d26 = cend(26) - cue(26)
# segments: (start in trailer, scene idx, source time at segment start, crop centre x, zoom)
SEG = [(0, 0, 2.2, 640, 1.0), (TL[1][0] - 0.1, 0, R.cue(2) + 0.3, 960, 1.0),
       (TL[2][0] - 0.1, 4, cue(26) + d26 * 0.55, 820, 1.0), (TL[3][0] - 0.1, 5, cue(27) - 0.4, 820, 1.0),
       (TL[4][0] - 0.1, 5, cue(34) + 0.3, 1010, 1.0), (TL[5][0] - 0.15, -1, 0, 0, 1)]
src_arr = np.zeros((1080, 1920, 4), np.uint8); src_surf = skia.Surface(src_arr)
def src_frame(si, ts):
    c = src_surf.getCanvas(); c.clear(col("#000000")); R.SCENES[si](c, ts, int(ts * 30)); src_surf.flushAndSubmit()
    return src_surf.makeImageSnapshot()
def headline(c, tt):
    a = eout(prog(tt, 0.05, 0.35))
    rrect(c, 60, 150, 960, 210, 22, P("#0a1220", 0.0))
    text(c, "THE OWL FILES · CASE #001", 540, 170, 30, "t", MUST, a, "c")
    text(c, "WHY IS THIS LAKE", 540, 250, 78, "b", PAPER, a, "c"); text(c, "FULL OF SKELETONS?", 540, 340, 78, "b", RED if int(tt * 2.2) % 2 == 0 or tt > 1.5 else PAPER, a, "c")
def caption(c, tt):
    for (s, e, txt) in TL:
        if s - 0.05 <= tt <= e + 0.12:
            words = txt.split(); chunks = []; cur = []
            for w in words:
                cur.append(w)
                if len(" ".join(cur)) > 22 or (w[-1] in ".?!" and len(cur) > 1): chunks.append(" ".join(cur)); cur = []
            if cur: chunks.append(" ".join(cur))
            tot = sum(len(x) + 3 for x in chunks); x = (tt - s) / (e - s) * tot; acc = 0; ch = chunks[-1]
            for q in chunks:
                if x < acc + len(q) + 3: ch = q; break
                acc += len(q) + 3
            font = skia.Font(TF["b"], 60); w = font.measureText(ch); cx = 600; y = 1525
            k = eout(prog(tt, s - 0.05, 0.15))
            rrect(c, cx - w / 2 - 28, y - 64, w + 56, 88, 20, P("#ffffff", 0.95 * k)); text(c, ch, cx, y, 60, "b", INK, k, "c"); return
def endcard(c, tt, t0, f):
    u = tt - t0
    c.drawRect(skia.Rect.MakeWH(VW, VH), P("#0b1420"))
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial((540, 760), 900, [col(TEAL, 0.35), col(TEAL, 0)])); c.drawRect(skia.Rect.MakeWH(VW, VH), p)
    k = eout(prog(u, 0, 0.35)); c.save(); c.translate(540, 760 + (1 - k) * 600); c.rotate(-3)
    rrect(c, -440, -300, 880, 600, 16, P("#d9ab5c")); rrect(c, -410, -270, 820, 540, 8, P(PAPER))
    text(c, "CASE #001", 0, -200, 34, "t", "#6b5a3c", anchor="c")
    text(c, "WHO WERE", 0, -90, 92, "b", INK, anchor="c"); text(c, "THEY?", 0, 20, 110, "b", RED, anchor="c")
    text(c, "Full case now on", 0, 130, 44, "s", "#6b5a3c", anchor="c"); text(c, "THE OWL FILES", 0, 210, 66, "b", INK, anchor="c")
    c.restore(); stamp(c, "WATCH NOW", 700, 1110, 64, u, 0.9, rot=-10)
    text(c, "@TheOwlFiles", 540, 300, 48, "b", MUST, eout(prog(u, 0.4, 0.3)), "c")
def frame(f):
    tt = f / FPS
    arr = np.zeros((VH, VW, 4), np.uint8); surf = skia.Surface(arr); c = surf.getCanvas(); c.clear(col("#0d2029"))
    si = max(k for k in range(len(SEG)) if SEG[k][0] <= tt)
    st, sc, ts0, cx, zm = SEG[si]
    if sc >= 0:
        img = src_frame(sc, ts0 + (tt - st))
        u = tt - st; z = 1.0 + 0.04 * u
        side = 1080 / z; srcR = skia.Rect.MakeXYWH(cx - side / 2, (1080 - side) / 2, side, side)
        dst = skia.Rect.MakeXYWH(0, 400, 1080, 1080)
        c.drawImageRect(img, srcR, dst, skia.SamplingOptions(skia.FilterMode.kLinear))
        g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([(0, 400), (0, 560)], [col("#0d2029", 1), col("#0d2029", 0)])); c.drawRect(skia.Rect.MakeXYWH(0, 400, 1080, 160), g)
        g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([(0, 1300), (0, 1480)], [col("#0d2029", 0), col("#0d2029", 1)])); c.drawRect(skia.Rect.MakeXYWH(0, 1300, 1080, 180), g)
        headline(c, tt)
        fl = 1 - prog(tt, st, 0.12)
        if si > 0 and fl > 0: c.drawRect(skia.Rect.MakeWH(VW, VH), P("#ffffff", 0.5 * fl))
    else:
        endcard(c, tt, st, f)
    # narrator owl
    e = env[min(f, nf - 1)]
    owl(c, 175 if sc >= 0 else 205, 1900, 0.62, tt, f, look=(0.7, -0.3), brow=0.5 if si in (2,) else (-0.7 if si == 4 else 0.2), talk=e, wing=1.0 if si == 5 else 0.0, prop="glass" if si < 5 else None)
    caption(c, tt)
    R.overlay_v(c, f) if hasattr(R, "overlay_v") else None
    c.drawImageRect(R.GRAIN[(f // 2) % 6], skia.Rect.MakeWH(VW, VH))
    o = prog(tt, TOTAL - 0.35, 0.35)
    if o > 0: c.drawRect(skia.Rect.MakeWH(VW, VH), P("#000000", o * 0.6))
    surf.flushAndSubmit(); return arr
if __name__ == "__main__":
    print("total", TOTAL)
    if sys.argv[1] == "still":
        from PIL import Image
        for x in sys.argv[2:]: Image.fromarray(frame(int(float(x) * FPS))[..., :3]).resize((540, 960)).save(f"tst_{float(x):05.1f}.jpg", quality=85)
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "tr/v.tmp.mp4"], stdin=subprocess.PIPE)
        for f in range(int(TOTAL * FPS)): p.stdin.write(frame(f).tobytes())
        p.stdin.close()
        if p.wait() == 0: os.rename("tr/v.tmp.mp4", "tr/v.mp4"); print("done")
