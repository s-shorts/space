import skia, numpy as np, json, subprocess, math, sys, os, random
W, H, FPS = 1920, 1080, 30
TL = json.load(open("timeline.json")); LN = TL["lines"]; SC = {int(k): v for k, v in TL["sc"].items()}
TOTAL = TL["total"]; TITLE_AT = TL["title"]; ENV = np.load("env.npy")
GF = "/usr/share/fonts/truetype/google-fonts/"
TF = {"b": skia.Typeface.MakeFromFile(GF + "Poppins-Bold.ttf"), "m": skia.Typeface.MakeFromFile(GF + "Poppins-Medium.ttf"),
      "r": skia.Typeface.MakeFromFile(GF + "Poppins-Regular.ttf"), "s": skia.Typeface.MakeFromFile(GF + "Lora-Italic-Variable.ttf"),
      "t": skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")}
NIGHT, PAPER, MUST, RED, TEAL, INK, CORK = "#0f1b2d", "#f3e6c8", "#e8a91c", "#d6402b", "#1f8a8a", "#1c2430", "#b78655"

def col(h, a=1.0):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * max(0, min(1, a))))
def P(h, a=1.0, stroke=0, blur=0, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(h, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, t0, d=0.4): return clamp((t - t0) / d)
def pop(t, t0, d=0.45):
    x = prog(t, t0, d)
    if x <= 0: return 0
    return 1 + 0.18 * math.sin(x * math.pi) * (1 - x) * 2.2 if x >= 1 else eout(x) * (1 + 0.25 * math.sin(x * math.pi))
def cue(i): return LN[i]["s"]
def cend(i): return LN[i]["e"]

def text(c, s, x, y, size, f="b", color=PAPER, a=1.0, anchor="l", track=0):
    font = skia.Font(TF[f], size); w = font.measureText(s)
    if anchor == "c": x -= w / 2
    elif anchor == "r": x -= w
    c.drawString(s, x, y, font, P(color, a)); return w
def wrap(s, size, f, maxw):
    font = skia.Font(TF[f], size); out = []; cur = ""
    for w in s.split():
        if font.measureText((cur + " " + w).strip()) > maxw and cur: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out
def para(c, s, x, y, size, f, color, maxw, a=1.0, lh=1.25, anchor="l"):
    for k, ln in enumerate(wrap(s, size, f, maxw)): text(c, ln, x, y + k * size * lh, size, f, color, a, anchor)
def rrect(c, x, y, w, h, r, paint): c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint)
def poly(c, pts, paint, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    c.drawPath(p, paint)
def grad_rect(c, x, y, w, h, c1, c2):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(x, y), (x, y + h)], [col(c1), col(c2)])); c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)

# ---------- overlays
rng = np.random.default_rng(3)
GRAIN = []
for k in range(6):
    g = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8); a = np.zeros((H // 2, W // 2, 4), np.uint8)
    a[..., 0] = a[..., 1] = a[..., 2] = g; a[..., 3] = 16; GRAIN.append(skia.Image.fromarray(a))
def overlay(c, f):
    c.drawImageRect(GRAIN[(f // 2) % 6], skia.Rect.MakeWH(W, H))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), 1150, [col("#000000", 0), col("#000000", 0), col("#000000", 0.5)], [0, 0.62, 1]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)

def caption(c, t):
    for l in LN:
        if l["s"] - 0.05 <= t <= l["e"] + 0.25:
            words = l["t"].split(); chunks = []; cur = []
            for w in words:
                cur.append(w)
                if len(" ".join(cur)) > 34 or (w[-1] in ".?!:" and len(cur) > 2): chunks.append(" ".join(cur)); cur = []
            if cur:
                if chunks and len(" ".join(cur)) < 10: chunks[-1] += " " + " ".join(cur)
                else: chunks.append(" ".join(cur))
            tot = sum(len(x) + 4 for x in chunks); x = (t - l["s"]) / (l["e"] - l["s"]) * tot; acc = 0; ch = chunks[-1]; st = 0
            for q in chunks:
                if x < acc + len(q) + 4: ch = q; st = acc; break
                acc += len(q) + 4
            font = skia.Font(TF["b"], 46); w = font.measureText(ch); cx = 830; y = 1004
            k = eout(clamp((x - st) / 2.5)) if st > 0 else eout(prog(t, l["s"] - 0.05, 0.15))
            c.save(); c.translate(cx, y - 16); c.scale(0.94 + 0.06 * k, 0.94 + 0.06 * k); c.translate(-cx, -(y - 16))
            rrect(c, cx - w / 2 - 30, y - 56, w + 60, 78, 18, P("#0a1220", 0.86 * k))
            text(c, ch, cx, y, 46, "b", "#ffffff", k, "c"); c.restore(); return

# ---------- the host: Professor Ullu
def owl(c, x, y, s, t, f, look=(0, 0), brow=0.0, wing=0.0, prop=None, talk=None, tilt=0.0):
    e = ENV[min(f, len(ENV) - 1)] if talk is None else talk
    e = 0.6 * e + 0.4 * ENV[max(0, min(f - 1, len(ENV) - 1))] if talk is None else e
    bob = math.sin(t * 2.1) * 5 + e * 7
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-150, -18, 150, 22), P("#000000", 0.28, blur=10))
    c.rotate(tilt + math.sin(t * 0.9) * 1.2); c.translate(0, -bob)
    sq = 1 + e * 0.025; c.scale(1 / sq, sq)
    BR, BR2, CREAM, ORG = "#8a5a3c", "#6e4530", "#f0dcb4", "#f08a24"
    # feet
    for sx in (-1, 1):
        for k in (-1, 0, 1): c.drawOval(skia.Rect.MakeXYWH(sx * 55 + k * 17 - 10, -14, 20, 30), P(ORG))
    # tail / body
    c.drawOval(skia.Rect.MakeLTRB(-150, -330, 150, 0), P(BR))
    c.drawOval(skia.Rect.MakeLTRB(-98, -250, 98, -6), P(CREAM))
    for r in range(4):
        for k in range(-2 + (r % 2 == 0), 3):
            px = k * 40 - (20 if r % 2 == 0 else 0) + 0; py = -190 + r * 40
            if abs(px) < 82 - r * 4:
                pth = skia.Path(); pth.moveTo(px - 11, py); pth.quadTo(px, py + 15, px + 11, py); c.drawPath(pth, P(BR2, 0.55, stroke=4))
    # wings
    lw = -18 - math.sin(t * 2.1) * 3
    c.save(); c.translate(-140, -235); c.rotate(lw + 28); c.drawOval(skia.Rect.MakeLTRB(-38, 0, 38, 185), P(BR2)); c.restore()
    c.save(); c.translate(140, -235); c.rotate(-28 - wing * 105 + math.sin(t * 7) * 4 * wing)
    c.drawOval(skia.Rect.MakeLTRB(-38, 0, 38, 185), P(BR2))
    if prop == "glass":
        c.translate(0, 175); c.rotate(160); c.drawLine(0, 0, 0, 70, P("#3a2a20", stroke=14))
        c.drawCircle(0, 115, 52, P("#bfe6ee", 0.35)); c.drawCircle(0, 115, 52, P(MUST, stroke=11)); c.drawLine(-22, 95, -8, 82, P("#ffffff", 0.8, stroke=6))
    if prop == "chai":
        c.translate(0, 180); c.rotate(28 + wing * 105)
        poly(c, [(-26, -40), (26, -40), (19, 14), (-19, 14)], P("#d9c9a8")); c.drawOval(skia.Rect.MakeLTRB(-26, -46, 26, -34), P("#8a4b22"))
        for k in range(2):
            sp = skia.Path(); ox = -8 + k * 16; yy = -52 - ((t * 30 + k * 20) % 40)
            sp.moveTo(ox, yy); sp.quadTo(ox + 8, yy - 10, ox, yy - 20); c.drawPath(sp, P("#ffffff", 0.35, stroke=4))
    c.restore()
    # scarf
    rrect(c, -118, -292, 236, 34, 16, P(RED)); poly(c, [(60, -262), (96, -262), (104, -196), (72, -200)], P(RED));
    for k in range(4): c.drawLine(-90 + k * 60, -290, -100 + k * 60, -260, P("#a82c1c", stroke=5))
    # head
    c.drawOval(skia.Rect.MakeLTRB(-168, -520, 168, -260), P(BR))
    poly(c, [(-150, -470), (-176, -572), (-84, -508)], P(BR)); poly(c, [(150, -470), (176, -572), (84, -508)], P(BR))
    c.drawOval(skia.Rect.MakeLTRB(-146, -470, 0, -300), P(CREAM)); c.drawOval(skia.Rect.MakeLTRB(0, -470, 146, -300), P(CREAM))
    bl = (t * 0.27 + 0.13) % 1.0; lid = 1.0 if bl > 0.972 else 0.0; bl2 = (t * 0.11) % 1.0; lid = 1.0 if 0.5 < bl2 < 0.512 else lid
    for sx in (-1, 1):
        ex = sx * 72; ey = -388
        c.drawCircle(ex, ey, 54, P("#ffffff"))
        if lid < 0.5:
            px = ex + look[0] * 20; py = ey + look[1] * 16
            c.drawCircle(px, py, 27, P(INK)); c.drawCircle(px + 9, py - 10, 9, P("#ffffff"))
        else:
            c.drawCircle(ex, ey, 54, P("#caa77e")); c.drawLine(ex - 40, ey + 6, ex + 40, ey + 6, P(BR2, stroke=6))
        c.drawCircle(ex, ey, 62, P(INK, stroke=9))
        # brows: brow>0 suspicious, <0 surprised
        c.save(); c.translate(ex, ey - 76 + min(0, brow) * 22); c.rotate(sx * (-brow * 22)); rrect(c, -44, -8, 88, 16, 8, P(BR2)); c.restore()
    c.drawLine(-12, -392, 12, -392, P(INK, stroke=9))
    # beak
    op = e * 26
    poly(c, [(-24, -340), (24, -340), (0, -306 + op * 0.2)], P(ORG))
    if op > 3: poly(c, [(-17, -334 + op * 0.3), (17, -334 + op * 0.3), (0, -306 + op)], P("#c2621a"))
    # detective cap
    c.save(); c.translate(0, -505); c.rotate(-5)
    pth = skia.Path(); pth.moveTo(-128, 0); pth.cubicTo(-120, -112, 120, -112, 128, 0); pth.close(); c.drawPath(pth, P("#51634a"))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    for k in range(-6, 8): c.drawLine(k * 34, -110, k * 34 - 40, 0, P("#3f4f3a", stroke=5)); c.drawLine(k * 34, -110, k * 34 + 40, 0, P("#65785b", 0.6, stroke=3))
    c.restore(); rrect(c, -150, -8, 300, 24, 12, P("#3a4835")); c.drawCircle(0, -86, 13, P("#3a4835")); c.restore()
    c.restore()

# ---------- props
def stamp(c, s, x, y, size, t, t0, rot=-9, color=RED):
    k = prog(t, t0, 0.16)
    if k <= 0: return
    sc = 2.6 - 1.6 * eout(k); font = skia.Font(TF["b"], size); w = font.measureText(s)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    rrect(c, -w / 2 - 34, -size * 0.92, w + 68, size * 1.5, 14, P(PAPER, 0.92 * k))
    rrect(c, -w / 2 - 34, -size * 0.92, w + 68, size * 1.5, 14, P(color, k, stroke=10))
    rrect(c, -w / 2 - 20, -size * 0.8, w + 40, size * 1.26, 8, P(color, k, stroke=3))
    c.drawString(s, -w / 2, size * 0.2, font, P(color, k)); c.restore()
def card(c, x, y, w, h, t, t0, rot=0.0, color=PAPER, pin=RED):
    k = pop(t, t0)
    if k <= 0: return False
    c.save(); c.translate(x + w / 2, y + h / 2); c.rotate(rot); c.scale(k, k); c.translate(-w / 2, -h / 2)
    rrect(c, 8, 12, w, h, 6, P("#000000", 0.3, blur=10)); rrect(c, 0, 0, w, h, 6, P(color))
    if pin: c.drawCircle(w / 2 + 3, 20, 13, P("#000000", 0.25)); c.drawCircle(w / 2, 16, 13, P(pin)); c.drawCircle(w / 2 - 4, 12, 4, P("#ffffff", 0.6))
    return True
def cross(c, x, y, r, t, t0, color=RED, w=16):
    k = prog(t, t0, 0.22)
    if k <= 0: return
    a = clamp(k * 2); b = clamp(k * 2 - 1)
    c.drawLine(x - r, y - r, x - r + 2 * r * a, y - r + 2 * r * a, P(color, stroke=w))
    if b > 0: c.drawLine(x + r, y - r, x + r - 2 * r * b, y - r + 2 * r * b, P(color, stroke=w))
def skull(c, x, y, s, a=1.0, color=PAPER, crack=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-50, -62, 50, 30), P(color, a)); rrect(c, -30, 6, 60, 46, 12, P(color, a))
    for sx in (-1, 1): c.drawOval(skia.Rect.MakeLTRB(sx * 22 - 14, -22, sx * 22 + 14, 10), P(INK, a * 0.85))
    poly(c, [(0, 8), (-7, 24), (7, 24)], P(INK, a * 0.85))
    for k in (-1, 0, 1): c.drawLine(k * 13, 36, k * 13, 52, P(INK, a * 0.6, stroke=3))
    if crack > 0:
        pts = [(4, -64), (-6, -50), (8, -42), (-2, -30), (6, -22)]; n = max(2, int(len(pts) * crack + 0.99))
        poly(c, pts[:n], P(RED, a, stroke=5), close=False)
    c.restore()
def person(c, x, y, s, color, a=1.0):
    c.drawCircle(x, y - 34 * s, 13 * s, P(color, a)); rrect(c, x - 15 * s, y - 20 * s, 30 * s, 44 * s, 12 * s, P(color, a))
def mountains(c, seed, base, amp, color, ox=0.0, snow=None, a=1.0):
    r = random.Random(seed); pts = [(-200, H)]; x = -200; peaks = []
    while x < W + 400:
        hgt = base - amp * (0.35 + 0.65 * r.random()); pts.append((x + ox, hgt)); peaks.append((x + ox, hgt)); x += 150 + r.random() * 170
        pts.append((x + ox, base - amp * 0.15 * r.random())); x += 120 + r.random() * 150
    pts.append((W + 600, H)); poly(c, pts, P(color, a))
    if snow:
        for (px, py) in peaks: poly(c, [(px, py), (px - 46, py + 62), (px - 18, py + 48), (px + 4, py + 72), (px + 24, py + 46), (px + 50, py + 66)], P(snow, a))
SNOW = [(random.Random(9).random() if False else rng.random(), rng.random(), rng.random()) for _ in range(160)]
def snowfall(c, t, a=0.8, n=160, speed=1.0):
    for (u, v, w) in SNOW[:n]:
        x = (u * W + math.sin(t * (0.6 + w) + u * 9) * 40 + t * 20) % W; y = (v * H + t * (60 + 120 * w) * speed) % H
        c.drawCircle(x, y, 1.5 + 3 * w, P("#ffffff", a * (0.3 + 0.6 * w)))
STARS = [(rng.random() * W, rng.random() * 520, rng.random()) for _ in range(140)]

def board(c, t, title=None, tag=None):
    grad_rect(c, 0, 0, W, H, "#173640", "#0d2029")
    for k in range(0, W, 96): c.drawLine(k, 0, k, H, P("#ffffff", 0.018, stroke=2))
    rrect(c, 52, 44, 1560, 880, 14, P("#000000", 0.35, blur=18)); rrect(c, 40, 30, 1560, 880, 14, P("#5a3b25")); rrect(c, 62, 52, 1516, 836, 6, P(CORK))
    r = random.Random(5)
    for k in range(500): c.drawCircle(62 + r.random() * 1516, 52 + r.random() * 836, 1 + r.random() * 2.5, P("#8f6238", 0.5))
    if title:
        w = skia.Font(TF["b"], 40).measureText(title) + 70
        rrect(c, 100, 84, w, 70, 6, P(INK)); text(c, title, 135, 133, 40, "b", MUST)
    if tag: text(c, tag, 1540, 132, 28, "t", "#3d2a1a", 0.8, "r")
    # lamp glow
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial((820, 120), 1200, [col("#ffe9b0", 0.16), col("#ffe9b0", 0)])); c.drawRect(skia.Rect.MakeWH(W, H), p)
def string(c, x1, y1, x2, y2, t, t0):
    k = ease(prog(t, t0, 0.5))
    if k > 0: c.drawLine(x1, y1, x1 + (x2 - x1) * k, y1 + (y2 - y1) * k, P(RED, 0.9, stroke=5))
def host_corner(c, t, f, look=(-0.6, -0.3), brow=0.0, wing=0.0, prop="glass"):
    owl(c, 1745, 1040, 0.62, t, f, look=look, brow=brow, wing=wing, prop=prop)
def fade_in(c, t, t0, d=0.3, color="#000000"):
    k = 1 - prog(t, t0, d)
    if k > 0: c.drawRect(skia.Rect.MakeWH(W, H), P(color, k))

# ================= SCENES =================
def s0(c, t, f):
    if t >= TITLE_AT: return title(c, t, f)
    z = 1 + 0.05 * (t / 16) + 0.28 * ease(prog(t, cue(2) - 0.4, 3.5)); c.save(); c.translate(W / 2, 800); c.scale(z, z); c.translate(-W / 2, -800)
    grad_rect(c, 0, 0, W, H, "#0b1530", "#3b5878")
    for (x, y, w) in STARS: c.drawCircle(x, y, 1 + 2 * w, P("#ffffff", 0.3 + 0.6 * abs(math.sin(t * (0.5 + w) + x))))
    c.drawCircle(1500, 190, 70, P("#f6efd8")); c.drawCircle(1500, 190, 120, P("#f6efd8", 0.12, blur=40))
    mountains(c, 11, 640, 420, "#22395a", ox=-t * 3, snow="#cfdcec"); mountains(c, 23, 760, 330, "#182a45", ox=-t * 7 - 80, snow="#aebfd6")
    poly(c, [(-200, H), (-200, 790), (300, 730), (700, 770), (1150, 740), (1700, 790), (2200, 750), (2200, H)], P("#dfe8f2"))
    poly(c, [(-200, H), (-200, 900), (400, 850), (1000, 880), (1500, 850), (2200, 900), (2200, H)], P("#c5d3e3"))
    # lake
    c.save(); c.translate(0, -24)
    lk = skia.Rect.MakeLTRB(620, 800, 1300, 960); c.drawOval(lk, P("#0d2a3f")); c.drawOval(skia.Rect.MakeLTRB(640, 812, 1280, 950), P("#12405a"))
    c.save(); lp = skia.Path(); lp.addOval(skia.Rect.MakeLTRB(640, 812, 1280, 950)); c.clipPath(lp, doAntiAlias=True)
    sk = ease(prog(t, cue(2) + 0.6, 2.2))
    if sk > 0:
        r = random.Random(4)
        for k in range(16):
            x = 680 + r.random() * 560; y = 835 + r.random() * 95; s = 0.28 + r.random() * 0.14
            aa = sk * (0.55 + 0.35 * math.sin(t * 2 + k)); c.drawCircle(x, y, 26, P("#9fe0e8", 0.18 * aa, blur=10)); skull(c, x, y, s, aa * 0.9, "#d8eef0")
            c.drawLine(x + 30, y + 4, x + 62, y + 12, P("#d8eef0", aa * 0.7, stroke=5))
    melt = ease(prog(t, cue(1) - 0.2, 3.0)); r = random.Random(8)
    for k in range(9):
        x = 700 + r.random() * 520; y = 830 + r.random() * 100; w = (70 + r.random() * 90) * (1 - 0.85 * melt)
        c.save(); c.translate(x + melt * (x - 960) * 0.25, y); c.rotate(r.random() * 40 - 20 + t * 2)
        poly(c, [(-w, -w * 0.18), (w * 0.2, -w * 0.3), (w, 0), (w * 0.3, w * 0.24), (-w * 0.6, w * 0.2)], P("#e9f3fb", 0.92 * (1 - melt * 0.5))); c.restore()
    c.restore(); c.restore()
    # ranger silhouette
    rx = -80 + 560 * eout(prog(t, 0.6, 6.5)); wk = math.sin(t * 7) * (1 - prog(t, 6.2, 0.8)); ry = 792
    c.save(); c.translate(rx, ry)
    c.drawLine(-6, -52, -6 - wk * 12, 0, P("#0a1322", stroke=11)); c.drawLine(6, -52, 6 + wk * 12, 0, P("#0a1322", stroke=11))
    rrect(c, -17, -112, 34, 66, 12, P("#0a1322")); c.drawCircle(0, -128, 15, P("#0a1322")); poly(c, [(-24, -134), (24, -134), (12, -146), (-12, -146)], P("#0a1322"))
    c.drawLine(14, -92, 32, -60, P("#0a1322", stroke=8)); c.drawLine(32, -110, 32, 4, P("#0a1322", stroke=5)); c.restore()
    snowfall(c, t); c.restore()
    # 1942 typewriter
    s = "1942"; n = int(clamp((t - 0.7) / 0.5) * 4)
    a = 1 - prog(t, cue(2) - 0.3, 0.6)
    if n: text(c, s[:n], 110, 210, 150, "t", PAPER, a)
    s2 = "ROOPKUND, UTTARAKHAND · INDIA"; n2 = int(clamp((t - 1.6) / 1.2) * len(s2))
    if n2: text(c, s2[:n2], 116, 268, 34, "t", MUST, a)
    if sk > 0.5: text(c, "Several hundred skeletons.", W / 2, 180, 76, "b", PAPER, ease(prog(t, cue(2) + 2.2, 0.6)), "c")
    fade_in(c, t, 0, 0.8)

def title(c, t, f):
    u = t - TITLE_AT; c.drawRect(skia.Rect.MakeWH(W, H), P("#0b1420"))
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), 900, [col(TEAL, 0.35), col(TEAL, 0)])); c.drawRect(skia.Rect.MakeWH(W, H), p)
    sh = math.sin(u * 60) * 14 * max(0, 1 - (u - 0.55) * 4) if u > 0.55 else 0
    c.save(); c.translate(sh, 0)
    k = eout(prog(u, 0.05, 0.4)); c.save(); c.translate(W / 2, H / 2 + (1 - k) * 700); c.rotate(-3)
    rrect(c, -640, -300, 1280, 620, 18, P("#000000", 0.4, blur=20)); poly(c, [(-640, -300), (-320, -300), (-280, -350), (-600, -350)], P("#c99a4d")); rrect(c, -640, -300, 1280, 620, 18, P("#d9ab5c"))
    rrect(c, -600, -262, 1200, 544, 8, P(PAPER))
    text(c, "THE OWL FILES  ·  CASE #001", -560, -196, 34, "t", "#6b5a3c")
    c.drawLine(-560, -170, 560, -170, P("#6b5a3c", 0.4, stroke=3))
    text(c, "THE SKELETON", 0, -30, 132, "b", INK, anchor="c"); text(c, "LAKE", 0, 110, 150, "b", RED, anchor="c")
    text(c, "an evidence-only investigation", 0, 200, 44, "s", "#6b5a3c", anchor="c")
    c.restore(); stamp(c, "UNSOLVED", 1380, 760, 84, u, 0.55, rot=-14); c.restore()
    owl(c, 300, 1060, 0.55, t, f, look=(0.7, -0.2), brow=0.5, talk=0)
    fade_in(c, u, 0, 0.2); o = prog(u, TL["TITLE"] + 0.5, 0.35)
    if o > 0: c.drawRect(skia.Rect.MakeWH(W, H), P("#000000", o))

def office(c, t):
    grad_rect(c, 0, 0, W, H, "#1b3f4a", "#102630")
    for k in range(0, W, 120): rrect(c, k + 40, 0, 6, 760, 0, P("#ffffff", 0.025))
    # window w/ mountains
    rrect(c, 110, 120, 420, 420, 10, P("#3a2416")); grad_rect(c, 130, 140, 380, 380, "#0b1530", "#3b5878")
    c.save(); c.clipRect(skia.Rect.MakeXYWH(130, 140, 380, 380)); c.scale(0.5, 0.5); c.translate(200, 300); mountains(c, 11, 640, 420, "#22395a", snow="#cfdcec"); c.restore()
    c.save(); c.clipRect(skia.Rect.MakeXYWH(130, 140, 380, 380)); snowfall(c, t, 0.7, 60, 0.5); c.restore()
    rrect(c, 314, 140, 12, 380, 0, P("#3a2416")); rrect(c, 130, 324, 380, 12, 0, P("#3a2416"))
    # shelf of files
    rrect(c, 1380, 300, 440, 16, 4, P("#3a2416"))
    for k, cl in enumerate([MUST, RED, TEAL, PAPER, "#51634a", MUST, RED]): rrect(c, 1400 + k * 56, 150 + (k * 37) % 40, 46, 150 - (k * 37) % 40, 4, P(cl))
    # lamp
    c.drawLine(960, 0, 960, 110, P("#111111", stroke=6)); poly(c, [(900, 170), (1020, 170), (990, 105), (930, 105)], P(MUST))
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial((960, 170), 900, [col("#ffe9b0", 0.30), col("#ffe9b0", 0)])); poly(c, [(900, 170), (1020, 170), (1650, H), (270, H)], p)
def desk(c):
    rrect(c, 0, 830, W, 260, 0, P("#4a2e1c")); rrect(c, 0, 830, W, 18, 0, P("#6b452b"))

def s1(c, t, f):
    office(c, t)
    wing = ease(prog(t, cue(3), 0.3)) * (1 - ease(prog(t, cue(3) + 1.6, 0.4))) + ease(prog(t, cue(6) - 0.1, 0.3)) * (1 - ease(prog(t, cend(6), 0.4)))
    brow = 0.7 * ease(prog(t, cue(4), 0.3)) * (1 - prog(t, cend(4) + 0.3, 0.3)) + 0.5 * prog(t, cue(6), 0.3) * (1 - prog(t, cend(6), 0.3))
    lk = (0.9, -0.1) if cue(6) < t < cend(6) + 0.3 else ((0, 0.1) if t < cue(7) else (-0.8, 0.2))
    owl(c, 960, 855, 0.98, t, f, look=lk, brow=brow, wing=wing, prop="chai" if t > cue(5) - 0.5 and not (cue(6) - 0.1 < t < cend(6)) else None)
    desk(c)
    # nameplate
    rrect(c, 700, 845, 520, 96, 10, P("#000000", 0.4, blur=8)); rrect(c, 700, 838, 520, 96, 10, P(INK)); rrect(c, 708, 846, 504, 80, 6, P(MUST, stroke=3))
    text(c, "PROF. ULLU", 960, 888, 46, "b", MUST, anchor="c"); text(c, "evidence-only detective", 960, 916, 22, "r", PAPER, 0.85, "c")
    # dictionary joke card
    if cue(4) + 0.3 < t < cue(5) - 0.1:
        if card(c, 1300, 380, 500, 250, t, cue(4) + 0.3, rot=4):
            text(c, "ullu", 36, 86, 60, "b", INK); text(c, "(noun, Hindi)", 190, 84, 28, "s", "#6b5a3c")
            text(c, "1. an owl.", 36, 142, 36, "m", INK); text(c, "2. ...you know what.", 36, 196, 36, "m", RED, prog(t, cue(4) + 1.2, 0.3)); c.restore()
    # evidence only: ghosts, aliens, forwards
    if t > cue(6) - 0.1 and t < cue(7) + 0.2:
        items = [("ghost", cue(6)), ("ufo", cue(6) + (cend(6) - cue(6)) * 0.3), ("fwd", cue(6) + (cend(6) - cue(6)) * 0.55)]
        for k, (nm, t0) in enumerate(items):
            x = 1330 + k * 190; y = 540
            if card(c, x - 80, y - 90, 160, 180, t, t0, rot=(k - 1) * 4, pin=None):
                if nm == "ghost":
                    pth = skia.Path(); pth.moveTo(40, 150); pth.lineTo(40, 80); pth.cubicTo(40, 20, 120, 20, 120, 80); pth.lineTo(120, 150); pth.lineTo(100, 135); pth.lineTo(80, 150); pth.lineTo(60, 135); pth.close()
                    c.drawPath(pth, P("#9aa7b5")); c.drawCircle(66, 78, 8, P(INK)); c.drawCircle(94, 78, 8, P(INK))
                elif nm == "ufo":
                    c.drawOval(skia.Rect.MakeLTRB(52, 50, 108, 100), P(TEAL)); c.drawOval(skia.Rect.MakeLTRB(22, 80, 138, 112), P("#6b7a8a")); poly(c, [(60, 112), (100, 112), (124, 160), (36, 160)], P(MUST, 0.5))
                else:
                    rrect(c, 46, 30, 68, 124, 10, P(INK)); rrect(c, 52, 40, 56, 100, 4, P("#25d366"))
                    for q in range(3): text(c, "Fwd:", 56, 66 + q * 28, 20, "b", "#ffffff")
                c.restore(); cross(c, x, y, 62, t, t0 + 0.35)
        text(c, "NOT EVIDENCE", 1520, 720, 40, "b", RED, prog(t, items[2][1] + 0.5, 0.2), "c")
    # case folder
    k = eout(prog(t, cue(7), 0.5))
    if k > 0:
        c.save(); c.translate(210 - (1 - k) * 700, 520); c.rotate(-6)
        rrect(c, 0, 0, 440, 280, 10, P("#000000", 0.35, blur=10)); rrect(c, -6, -8, 440, 280, 10, P("#d9ab5c")); rrect(c, 14, 14, 400, 240, 6, P(PAPER))
        text(c, "CASE #001", 40, 70, 30, "t", "#6b5a3c"); text(c, "Skeleton Lake", 40, 130, 48, "b", INK); text(c, "of Roopkund", 40, 186, 48, "b", RED); c.restore()
    fade_in(c, t, SC[1], 0.35)

def s2(c, t, f):
    grad_rect(c, 0, 0, W, H, "#7fb1d6", "#dcebf5")
    c.drawCircle(1620, 170, 80, P("#fff6d6")); c.drawCircle(1620, 170, 150, P("#fff6d6", 0.25, blur=40))
    base = 900; top = 150; M = 5600.0
    def Y(m): return base - (m / M) * (base - top)
    for m in range(1000, 5601, 1000):
        c.drawLine(150, Y(m), W, Y(m), P("#ffffff", 0.35, stroke=2)); text(c, f"{m:,} m", 138, Y(m) + 10, 26, "m", "#27425c", 0.8, "r")
    # Alps peak (Mont Blanc)
    k1 = eout(prog(t, cue(9) - 0.2, 0.7));
    if k1 > 0:
        px = 620; py = Y(4806 * k1); poly(c, [(280, base), (px - 120, py + 150), (px, py), (px + 150, py + 190), (980, base)], P("#8ea4bd"))
        poly(c, [(px, py), (px - 52, py + 66), (px - 16, py + 50), (px + 10, py + 78), (px + 58, py + 72)], P("#ffffff"))
        if k1 > 0.95:
            a = prog(t, cue(9) + 0.5, 0.3) * (1 - prog(t, cue(10) - 0.4, 0.3)); rrect(c, px - 190, py - 108, 380, 84, 12, P(INK, 0.9 * a)); text(c, "Mont Blanc · 4,806 m", px, py - 70, 30, "b", PAPER, a, "c"); text(c, "tallest peak of the Alps", px, py - 38, 22, "r", PAPER, a * 0.8, "c")
    # Himalaya ridge with Roopkund
    k0 = eout(prog(t, SC[2] + 0.2, 0.9)); rx = 1250; ry = Y(5029)
    off = (1 - k0) * 800
    c.save(); c.translate(0, off)
    poly(c, [(820, base), (1000, Y(3400)), (1110, Y(4300)), (1200, ry + 6), (1300, ry + 6), (1390, Y(5500)), (1500, Y(4700)), (1640, Y(5300)), (1790, Y(4200)), (W + 50, Y(4600)), (W + 50, base)], P("#4f6a8c"))
    poly(c, [(1390, Y(5500)), (1350, Y(5500) + 60), (1380, Y(5500) + 46), (1400, Y(5500) + 74), (1432, Y(5500) + 52)], P("#ffffff"))
    poly(c, [(1640, Y(5300)), (1598, Y(5300) + 60), (1630, Y(5300) + 44), (1650, Y(5300) + 70), (1682, Y(5300) + 50)], P("#ffffff"))
    c.drawOval(skia.Rect.MakeLTRB(1205, ry - 4, 1295, ry + 14), P("#12405a")); c.restore()
    rrect(c, 0, base, W, H - base, 0, P("#3d5a45"))
    a = prog(t, cue(8) + 1.4, 0.3)
    if a > 0:
        pl = 1 + 0.25 * abs(math.sin(t * 4)); c.drawCircle(rx, ry + 4, 30 * pl, P(RED, 0.25 * a)); c.drawCircle(rx, ry + 4, 12, P(RED, a))
        c.drawLine(rx, ry - 14, rx, ry - 90, P(RED, a, stroke=4)); rrect(c, rx - 210, ry - 186, 420, 96, 12, P(RED, a)); text(c, "ROOPKUND · 5,029 m", rx, ry - 140, 34, "b", "#ffffff", a, "c"); text(c, "Uttarakhand, India", rx, ry - 106, 24, "r", "#ffffff", a * 0.9, "c")
        if k1 > 0.95:
            b = prog(t, cue(9) + 1.4, 0.3) * (1 - prog(t, cue(10) - 0.4, 0.3)); c.drawLine(640, Y(4806), 1190, Y(4806), P(INK, 0.5 * b, stroke=3));
            rrect(c, 800, Y(4806) + 14, 250, 50, 10, P(MUST, b)); text(c, "+223 m higher", 925, Y(4806) + 49, 28, "b", INK, b, "c")
    # lake inset
    ki = pop(t, cue(10) - 0.1)
    if ki > 0:
        cx, cy = 480, 470; dim = prog(t, cue(13) - 0.2, 0.3)
        c.save(); c.translate(cx, cy); c.scale(ki, ki)
        c.drawCircle(0, 0, 330, P("#000000", 0.25, blur=16)); c.drawCircle(0, 0, 322, P(PAPER)); c.drawCircle(0, 0, 300, P("#e7eef5"))
        c.drawOval(skia.Rect.MakeLTRB(-170, -90, 170, 90), P("#12405a")); c.drawOval(skia.Rect.MakeLTRB(-150, -74, 150, 74), P("#1b5a7a"))
        a2 = prog(t, cue(10) + 0.8, 0.3); c.drawLine(-170, -205, 170, -205, P(INK, a2, stroke=5))
        for sx in (-1, 1): poly(c, [(sx * 170, -205), (sx * 150, -217), (sx * 150, -193)], P(INK, a2))
        text(c, "about 40 m wide", 0, -226, 36, "b", INK, a2, "c")
        # owl walks round
        w0 = cue(11) - 0.2
        if t > w0:
            ang = -math.pi / 2 + min(1, (t - w0) / (cend(11) - w0)) * 2 * math.pi; ox = math.cos(ang) * 215; oy = math.sin(ang) * 128
            c.restore(); owl(c, cx + ox * ki, cy + oy * ki + 46, 0.17, t * 3, f, talk=0.6 * abs(math.sin(t * 9)), look=(math.cos(ang + 1.5), 0)); c.save(); c.translate(cx, cy)
            if (t - w0) > (cend(11) - w0) * 0.55: text(c, "huff... puff...", ox + (40 if ox < 60 else -200), oy + 30, 26, "s", RED, 1)
        # bones
        b0 = cue(12)
        if t > b0:
            r = random.Random(2)
            for k in range(46):
                ang = r.random() * 6.28; rad = 1.12 + r.random() * 0.45; bx = math.cos(ang) * 170 * rad; by = math.sin(ang) * 95 * rad + 20
                if prog(t, b0 + k * 0.035, 0.1) > 0:
                    c.save(); c.translate(bx, by); c.rotate(r.random() * 180); c.drawLine(-9, 0, 9, 0, P("#fffdf5", stroke=5)); c.drawCircle(-10, 0, 4, P("#fffdf5")); c.drawCircle(10, 0, 4, P("#fffdf5")); c.restore()
            a3 = prog(t, b0 + 1.2, 0.3); rrect(c, -230, 196, 460, 66, 12, P(INK, a3)); text(c, "several hundred people", 0, 240, 34, "b", MUST, a3, "c")
        c.restore()
    q = cue(13)
    if t > q:
        for k, (s, x, y, rot, t0) in enumerate([("WHO?", 1010, 500, -6, q), ("HOW?", 1010, 700, 5, q + (cend(13) - q) * 0.4)]):
            kk = pop(t, t0)
            if kk > 0:
                c.save(); c.translate(x, y); c.rotate(rot); c.scale(kk, kk); w = skia.Font(TF["b"], 150).measureText(s)
                rrect(c, -w / 2 - 40, -140, w + 80, 190, 20, P(INK)); text(c, s, 0, 0, 150, "b", MUST, anchor="c"); c.restore()
    host_corner(c, t, f, look=(-0.7, -0.4), brow=-0.5 * prog(t, cue(12), 0.3))
    fade_in(c, t, SC[2], 0.35)

def s3(c, t, f):
    board(c, t, "THEORY 1", "CASE #001 · ROOPKUND")
    if card(c, 130, 200, 640, 400, t, cue(14), rot=-2):
        text(c, "WARTIME, 1942", 40, 78, 28, "t", "#6b5a3c"); text(c, "Japanese soldiers", 40, 142, 54, "b", INK); text(c, "sneaking into India?", 40, 202, 54, "b", INK)
        # helmet doodle
        pth = skia.Path(); pth.moveTo(60, 340); pth.cubicTo(70, 250, 210, 250, 220, 340); pth.close(); c.drawPath(pth, P("#51634a")); rrect(c, 44, 334, 196, 18, 9, P("#3a4835"))
        text(c, "?", 300, 350, 130, "b", MUST); c.restore()
    if card(c, 860, 240, 560, 220, t, cue(15), rot=3, color="#fffdf5"):
        text(c, "LAB NOTE", 34, 62, 26, "t", "#6b5a3c"); text(c, "Bones: far too old.", 34, 126, 50, "b", RED); text(c, "centuries, not months", 34, 176, 30, "s", INK); c.restore()
    string(c, 770, 400, 860, 350, t, cue(15) + 0.2)
    stamp(c, "DISMISSED", 450, 480, 90, t, cue(16) + (cend(16) - cue(16)) * 0.72, rot=-12)
    for k, (nm, t0) in enumerate([("Epidemic?", 0.22), ("Landslide?", 0.5), ("Mass ritual?", 0.72)]):
        tt = cue(17) + (cend(17) - cue(17)) * t0; x = 130 + k * 330
        if card(c, x, 640, 300, 190, t, tt, rot=(k - 1) * 3):
            text(c, nm, 150, 84, 42, "b", INK, anchor="c"); c.restore()
        stamp(c, "NO PROOF", x + 150, 778, 34, t, cue(18) + 0.25 + k * 0.28, rot=-8 + k * 6)
    # chai rule
    tt = cue(18) + (cend(18) - cue(18)) * 0.55
    if card(c, 1150, 540, 400, 300, t, tt, rot=5, color=MUST, pin=INK):
        text(c, "OFFICE RULE", 200, 70, 28, "t", INK, anchor="c"); text(c, "No proof,", 200, 150, 60, "b", INK, anchor="c"); text(c, "no chai.", 200, 226, 60, "b", "#7a2313", anchor="c"); c.restore()
    host_corner(c, t, f, look=(-0.8, -0.2), brow=0.6 * prog(t, cue(16), 0.3), prop="chai" if t > tt else "glass", wing=ease(prog(t, tt, 0.3)) * 0.5)
    fade_in(c, t, SC[3], 0.35)

def s4(c, t, f):
    board(c, t, "THEORY 2 · THE HAILSTORM", "CASE #001 · ROOPKUND")
    folk = t > cue(23) - 0.3
    if not folk:
        if card(c, 120, 200, 520, 640, t, cue(20) - 0.2, rot=-2):
            text(c, "EXHIBIT A", 36, 70, 28, "t", "#6b5a3c")
            cr = prog(t, cue(20) + 1.6, 0.6); skull(c, 260, 330, 2.6, 1, "#e9dcc0", crack=cr)
            a = prog(t, cue(20) + 2.6, 0.3); yy = 60 + 60 * ease(prog(t, cue(20) + 2.6, 0.5)); c.drawLine(280, yy, 280, yy + 70, P(RED, a, stroke=8)); poly(c, [(262, yy + 62), (298, yy + 62), (280, yy + 92)], P(RED, a))
            text(c, "struck from ABOVE", 260, 530, 40, "b", RED, prog(t, cue(20) + 3.2, 0.3), "c"); text(c, "by something ROUND", 260, 584, 40, "b", INK, prog(t, cue(20) + 4.2, 0.3), "c"); c.restore()
        if t < cue(22) - 0.3 and card(c, 1010, 210, 520, 200, t, cue(20) + 1.0, rot=2, color="#fffdf5"):
            text(c, "FIELD NOTE", 34, 60, 26, "t", "#6b5a3c"); text(c, "Found on some skulls:", 34, 112, 34, "m", INK); text(c, "short, deep cracks", 34, 160, 40, "b", RED); c.restore()
        d = cend(21) - cue(21)
        for k, (nm, fr) in enumerate([("sword", 0.0), ("arrow", 0.17)]):
            x = 760 + k * 230; tt = cue(21) + d * fr
            if card(c, x - 90, 210, 190, 200, t, tt, rot=(k * 2 - 1) * 4, pin=None):
                if nm == "sword": c.drawLine(50, 160, 140, 44, P("#8d99a6", stroke=14)); c.drawLine(40, 130, 84, 164, P("#5a3b25", stroke=12))
                else: c.drawLine(40, 160, 150, 50, P("#5a3b25", stroke=8)); poly(c, [(160, 40), (126, 52), (148, 74)], P("#8d99a6"))
                c.restore(); cross(c, x + 5, 310, 70, t, tt + 0.3)
        tt = cue(21) + d * 0.36
        if card(c, 700, 450, 520, 390, t, tt, rot=2, color="#fffdf5"):
            text(c, "HAILSTONE", 130, 70, 28, "t", "#6b5a3c", anchor="c"); text(c, "CRICKET BALL", 390, 70, 28, "t", "#6b5a3c", anchor="c")
            c.drawCircle(130, 200, 92, P("#cfe6f2")); c.drawCircle(130, 200, 92, P("#8fb5c9", stroke=6)); c.drawCircle(100, 170, 22, P("#ffffff", 0.8))
            b = pop(t, cue(21) + d * 0.72)
            if b > 0:
                c.save(); c.translate(390, 200); c.scale(b, b); c.drawCircle(0, 0, 92, P("#b3261a")); pth = skia.Path(); pth.moveTo(-30, -86); pth.quadTo(10, 0, -30, 86); c.drawPath(pth, P("#ffffff", stroke=5)); pth = skia.Path(); pth.moveTo(-14, -90); pth.quadTo(26, 0, -14, 90); c.drawPath(pth, P("#ffffff", stroke=5)); c.restore()
                text(c, "≈", 260, 222, 80, "b", INK, anchor="c"); text(c, "same size!", 260, 350, 44, "b", RED, anchor="c")
            c.restore()
        # ridge storm
        if card(c, 1260, 200, 290, 640, t, cue(22) - 0.2, rot=3, color="#22395a"):
            c.save(); c.clipRect(skia.Rect.MakeWH(290, 640))
            poly(c, [(0, 640), (0, 520), (70, 470), (150, 500), (230, 450), (290, 480), (290, 640)], P("#dfe8f2"))
            for k in range(5): person(c, 50 + k * 46, 470 + [38, 10, 28, -4, 18][k], 0.7, "#0a1322")
            for k in range(26):
                u = (k * 0.618) % 1; v = ((k * 0.37) + t * (1.3 + (k % 5) * 0.2)) % 1; x = u * 330 - 20 - v * 40; y = v * 520 + 40
                c.drawLine(x + 10, y - 26, x, y, P("#ffffff", 0.35, stroke=3)); c.drawCircle(x, y, 7 + (k % 3) * 2, P("#e9f3fb"))
            text(c, "nowhere to hide", 145, 600, 30, "b", MUST, anchor="c"); c.restore(); c.restore()
    else:
        if card(c, 130, 190, 1400, 660, t, cue(23) - 0.2, rot=-1, color="#1a2a4a", pin=MUST):
            c.save(); c.clipRect(skia.Rect.MakeWH(1400, 660))
            for k in range(60): c.drawCircle((k * 197) % 1400, (k * 89) % 380, 2 + (k % 3), P("#ffffff", 0.3 + 0.5 * abs(math.sin(t + k))))
            poly(c, [(0, 660), (0, 520), (300, 420), (520, 250), (640, 330), (760, 180), (900, 360), (1100, 300), (1400, 480), (1400, 660)], P("#31466e"))
            poly(c, [(760, 180), (700, 262), (740, 246), (770, 286), (812, 250)], P("#e9f3fb")); poly(c, [(520, 250), (476, 310), (510, 296), (540, 326), (566, 290)], P("#e9f3fb"))
            a = prog(t, cue(24) + 0.3, 0.4); text(c, "THE FOLK SONG", 60, 80, 30, "t", MUST, a)
            for k in range(5):
                nx = 80 + k * 70 + math.sin(t * 2 + k) * 10; ny = 150 + math.sin(t * 3 + k * 1.3) * 22
                c.drawCircle(nx, ny, 13, P(MUST, a)); c.drawLine(nx + 12, ny, nx + 12, ny - 50, P(MUST, a, stroke=5))
            a2 = prog(t, cue(24) + 2.2, 0.4)
            # crown
            poly(c, [(190, 520), (190, 450), (220, 485), (250, 440), (280, 485), (310, 450), (310, 520)], P(MUST, a2)); text(c, "a king angers", 250, 580, 34, "b", PAPER, a2, "c"); text(c, "the goddess Nanda Devi", 250, 622, 30, "m", PAPER, a2, "c")
            if t > cue(25):
                for k in range(34):
                    u = (k * 0.618) % 1; v = ((k * 0.29) + (t - cue(25)) * (0.9 + (k % 5) * 0.15)) % 1; x = 420 + u * 950 - v * 60; y = v * 620
                    c.drawLine(x + 14, y - 40, x, y, P("#ffffff", 0.3, stroke=4)); c.drawCircle(x, y, 10 + (k % 3) * 3, P("#dcebf5"))
                a3 = prog(t, cue(25) + 1.3, 0.3); rrect(c, 800, 520, 520, 96, 14, P(INK, 0.85 * a3)); text(c, "“hailstones hard as iron”", 1060, 582, 36, "s", PAPER, a3, "c")
            c.restore(); c.restore()
        d = cend(26) - cue(26); a = prog(t, cue(26) + d * 0.3, 0.2)
        if a > 0: c.drawRect(skia.Rect.MakeXYWH(62, 52, 1516, 836), P("#0d2029", 0.45 * a)); text(c, "One storm. One tragedy.", 820, 330, 76, "b", PAPER, a, "c")
        stamp(c, "CASE CLOSED", 820, 600, 150, t, cue(26) + d * 0.78, rot=-7)
    host_corner(c, t, f, look=(-0.8, -0.3), brow=-0.6 * prog(t, cue(23), 0.3) * (1 - prog(t, cue(26), 0.3)))
    fade_in(c, t, SC[4], 0.35)

GRID = [(k % 10, k // 10) for k in range(38)]
def s5(c, t, f):
    sh = 0
    if cue(29) + 0.5 < t < cue(29) + 1.3: sh = math.sin(t * 70) * 16 * (1 - (t - cue(29) - 0.5) / 0.8)
    c.save(); c.translate(sh, -sh * 0.4)
    board(c, t, "2019 · THE DNA TEST", "CASE #001 · ROOPKUND")
    if t < cue(28) - 0.2:
        c.drawRect(skia.Rect.MakeXYWH(62, 52, 1516, 836), P("#0d2029", 0.45))
        c.save(); c.translate(820, 470); c.rotate(-7); font = skia.Font(TF["b"], 150); w = font.measureText("CASE CLOSED")
        rrect(c, -w / 2 - 34, -138, w + 68, 225, 14, P(PAPER, 0.92)); rrect(c, -w / 2 - 34, -138, w + 68, 225, 14, P(RED, 1, stroke=10)); c.drawString("CASE CLOSED", -w / 2, 30, font, P(RED))
        k = prog(t, cue(27) + 0.1, 0.25); c.drawLine(-w / 2 - 60, -30, -w / 2 - 60 + (w + 120) * k, -30, P(INK, stroke=22)); c.restore()
        text(c, "...or so we thought.", 820, 760, 80, "s", MUST, prog(t, cue(27) + 0.3, 0.3), "c")
    else:
        # dna helix panel
        if card(c, 110, 190, 300, 610, t, cue(28) - 0.2, rot=-2, color=INK, pin=MUST):
            for k in range(20):
                y = 60 + k * 26; ph = t * 2.2 + k * 0.5; x1 = 150 + math.sin(ph) * 90; x2 = 150 - math.sin(ph) * 90; z = math.cos(ph)
                c.drawLine(x1, y, x2, y, P("#ffffff", 0.25, stroke=3)); c.drawCircle(x1, y, 9 + 4 * z, P(MUST)); c.drawCircle(x2, y, 9 - 4 * z, P(TEAL))
            c.restore()
        a = prog(t, cue(28) + 2.0, 0.3); text(c, "38 skeletons · genome-wide DNA", 470, 232, 40, "b", INK, a); text(c, "Harney et al., Nature Communications, 2019", 470, 274, 26, "s", "#3d2a1a", a)
        # people
        gA = ease(prog(t, cue(30), 0.9)); gB = ease(prog(t, cue(32), 0.9)); gC = ease(prog(t, cue(35), 0.7))
        app = cue(28) + 3.2
        for k, (gx, gy) in enumerate(GRID):
            if prog(t, app + k * 0.03, 0.1) <= 0: continue
            x0 = 620 + gx * 78; y0 = 400 + gy * 80
            if k < 23: g = gA; cl = MUST; j = k; x1 = 480 + (j % 8) * 46; y1 = 420 + (j // 8) * 78
            elif k < 37: g = gB; cl = TEAL; j = k - 23; x1 = 960 + (j % 7) * 46; y1 = 420 + (j // 7) * 78
            else: g = gC; cl = RED; x1 = 1400; y1 = 440
            x = x0 + (x1 - x0) * g; y = y0 + (y1 - y0) * g; s = 1.15 - 0.3 * max(gA if k < 23 else 0, gB if 23 <= k < 37 else 0, gC if k == 37 else 0)
            if k >= 23 and gA > 0 and (gB if k < 37 else gC) == 0: s *= 1 - 0.0
            person(c, x, y, s, cl if g > 0.05 else "#e9dcc0")
        def lab(x, y, n, s1, s2, cl, t0, w=380):
            a = pop(t, t0)
            if a > 0:
                c.save(); c.translate(x + w / 2, y + 60); c.scale(a, a); c.translate(-w / 2, -60)
                rrect(c, 0, 0, w, 120, 12, P(INK)); rrect(c, 0, 0, 14, 120, 6, P(cl)); text(c, n, 34, 82, 76, "b", cl); nw = skia.Font(TF["b"], 76).measureText(n)
                text(c, s1, 52 + nw, 52, 27, "b", PAPER); text(c, s2, 52 + nw, 90, 25, "r", PAPER, 0.85); c.restore()
        lab(460, 700, "23", "South Asian", "ancestry", MUST, cue(30) + 0.6, 400)
        lab(940, 700, "14", "Eastern Mediterranean", "closest: Greece & Crete" if t > cue(33) + 0.5 else "ancestry", TEAL, cue(32) + 0.6, 480)
        lab(1300, 520, "1", "Southeast", "Asian", RED, cue(35) + 0.5, 250)
        # dates
        def date(x, s, cl, t0):
            a = pop(t, t0)
            if a > 0: c.save(); c.translate(x, 356); c.scale(a, a); rrect(c, -130, -40, 260, 64, 32, P(cl)); text(c, s, 0, 6, 36, "b", INK if cl != RED else "#ffffff", anchor="c"); c.restore()
        date(650, "~ 800 CE", MUST, cue(31) + 0.9); date(1120, "~ 1800 CE", TEAL, cue(34) + 0.8)
        g = ease(prog(t, cue(34) + 1.8, 0.6))
        if g > 0:
            y = 330; c.drawLine(790, y, 790 + 190 * g, y, P(RED, stroke=6))
            if g > 0.95: poly(c, [(990, y), (968, y - 14), (968, y + 14)], P(RED)); text(c, "1,000 years", 885, y - 18, 30, "b", RED, anchor="c")
        a = prog(t, cue(36) + 0.4, 0.3)
        if a > 0:
            rrect(c, 440, 232, 0, 0, 12, P(RED, a)); rrect(c, 1010, 560, 0, 0, 0, P(RED,a)); rrect(c, 440, 836, 1100, 0, 0, P(RED,a)); c.drawRect(skia.Rect.MakeXYWH(62, 826, 1516, 62), P(RED, a)); text(c, "NOT one tragedy — several, 1,000 years apart", 820, 872, 40, "b", "#ffffff", a, "c")
    c.restore()
    br = -0.9 if cue(29) < t < cue(30) or cue(34) < t < cue(35) else 0.3 * (t > cue(32))
    host_corner(c, t, f, look=(-0.8, -0.3), brow=br, wing=1.0 if cue(34) + 1.2 < t < cend(34) + 0.4 else 0)
    if cue(29) + 0.5 < t < cue(29) + 0.75: c.drawRect(skia.Rect.MakeWH(W, H), P("#ffffff", 0.7 * (1 - (t - cue(29) - 0.5) / 0.25)))
    fade_in(c, t, SC[5], 0.35)

def s6(c, t, f):
    board(c, t, "THE BIG QUESTION", "CASE #001 · ROOPKUND")
    a = prog(t, cue(37), 0.3); text(c, "Greek-like ancestry... at 5,000 m in the Himalayas?", 110, 236, 50, "b", INK, a)
    text(c, "around 1800 CE", 110, 284, 32, "s", "#3d2a1a", prog(t, cue(37) + 2, 0.3))
    if cue(37) + 0.8 < t < cue(38) - 0.15:
        for k in range(14):
            kk = pop(t, cue(37) + 1.0 + k * 0.08)
            if kk > 0: person(c, 250 + k * 62, 600 - k * 14 + (1 - kk) * 30, 1.5, TEAL)
        kk = pop(t, cue(37) + 2.6)
        if kk > 0: c.save(); c.translate(1290, 560); c.scale(kk, kk); c.rotate(8); text(c, "?", 0, 100, 380, "b", RED, anchor="c"); c.restore()
    rows = [("Trade?", "Not on any major trade route", cue(38)), ("Disease?", "No sign of bacterial infection", cue(39)), ("War?", "No weapons ever found", cue(40)), ("Records?", "None found — so far", cue(43))]
    for k, (q, ans, t0) in enumerate(rows):
        y = 320 + k * 112
        if card(c, 110, y, 900, 92, t, t0 - 0.1, rot=0, pin=None):
            text(c, q, 34, 62, 46, "b", INK); d = (cend(38 + k if k < 3 else 43) - t0)
            ta = t0 + (0.9 if k < 3 else d * 0.5); text(c, ans, 300, 60, 32, "m", "#3d2a1a", prog(t, ta, 0.3)); c.restore()
            cross(c, 1070, y + 46, 30, t, ta + 0.2, w=14)
    # same lake chips
    chips = [("Different DNA", cue(42)), ("Different food", cue(42) + (cend(42) - cue(42)) * 0.3), ("Different century", cue(42) + (cend(42) - cue(42)) * 0.55)]
    if t > cue(41) - 0.2:
        if card(c, 1150, 300, 400, 520, t, cue(41) - 0.2, rot=3, color=INK, pin=MUST):
            text(c, "ISOTOPE TEST", 200, 70, 26, "t", MUST, anchor="c"); text(c, "even the diet", 200, 118, 32, "m", PAPER, anchor="c"); text(c, "was different", 200, 158, 32, "m", PAPER, anchor="c")
            for k, (s, t0) in enumerate(chips):
                kk = pop(t, t0)
                if kk > 0: c.save(); c.translate(200, 230 + k * 76); c.scale(kk, kk); rrect(c, -170, -30, 340, 60, 30, P([MUST, TEAL, RED][k])); text(c, s, 0, 11, 30, "b", "#ffffff" if k else INK, anchor="c"); c.restore()
            kk = pop(t, cue(42) + (cend(42) - cue(42)) * 0.8)
            if kk > 0: c.save(); c.translate(200, 468); c.scale(kk, kk); text(c, "SAME LAKE.", 0, 0, 52, "b", PAPER, anchor="c"); c.restore()
            c.restore()
    host_corner(c, t, f, look=(-0.8, -0.2), brow=0.5, wing=0)
    fade_in(c, t, SC[6], 0.35)

def s7(c, t, f):
    end = cue(52) - 0.5
    if t < end:
        board(c, t, "THE VERDICT", "CASE #001 · ROOPKUND")
        if t < cue(46) - 0.2:
            if card(c, 130, 200, 900, 330, t, cue(44) - 0.1, rot=-1.5):
                text(c, "“", 30, 120, 150, "s", MUST); text(c, "Still not clear what brought them", 110, 110, 44, "s", INK); text(c, "here — or how they died.", 110, 170, 44, "s", INK)
                text(c, "— Niraj Rai, senior author of the 2019 study", 110, 250, 28, "m", "#6b5a3c"); text(c, "(paraphrased)", 110, 288, 22, "r", "#6b5a3c"); c.restore()
            if card(c, 300, 580, 1100, 250, t, cue(45) - 0.1, rot=1, color=INK, pin=MUST):
                text(c, "TESTED SO FAR", 40, 66, 26, "t", MUST); g = ease(prog(t, cue(45) + 0.5, 1.0))
                rrect(c, 40, 100, 1020, 56, 28, P("#33414f")); rrect(c, 40, 100, 20 + 110 * g, 56, 28, P(MUST))
                text(c, "38", 60 + 130 * g, 142, 40, "b", MUST, g); text(c, "of several hundred skeletons", 1050, 210, 34, "m", PAPER, prog(t, cue(45) + 1.8, 0.3), "r"); c.restore()
        elif t < cue(50) - 0.2:
            for k, (a_, b_, cl, t0) in enumerate([("Hailstorm", "PROBABLE — for some", MUST, cue(47)), ("Everyone else", "UNSOLVED", RED, cue(48))]):
                if card(c, 150, 230 + k * 250, 1300, 200, t, t0 - 0.1, rot=(-1.5, 1.5)[k]):
                    text(c, a_, 50, 126, 70, "b", INK); c.restore(); stamp(c, b_, 1060, 330 + k * 250, 56 if k == 0 else 84, t, t0 + (0.6 if k == 0 else 0.7), rot=(-5, 6)[k], color=("#b07a00", RED)[k])
            a = prog(t, cue(49), 0.4)
            if a > 0: rrect(c, 300, 760, 1000, 90, 14, P(INK, a)); text(c, "The lake is keeping its secret.", 800, 820, 44, "s", PAPER, a, "c")
        else:
            if card(c, 170, 220, 1250, 360, t, cue(50) - 0.1, rot=-1, color="#fffdf5"):
                text(c, "YOUR THEORY?", 50, 80, 30, "t", "#6b5a3c"); s = "I think what really happened was"; n = int(clamp((t - cue(50) - 0.4) / 2.2) * len(s))
                rrect(c, 50, 120, 1150, 110, 14, P("#eef1f4")); text(c, s[:n] + ("|" if int(t * 2) % 2 else ""), 80, 190, 42, "m", INK)
                rrect(c, 950, 260, 250, 66, 33, P(TEAL)); text(c, "Comment", 1075, 305, 32, "b", "#ffffff", anchor="c"); c.restore()
            if card(c, 520, 610, 700, 220, t, cue(51) - 0.1, rot=2, color=MUST, pin=INK):
                text(c, "PRIZE", 350, 62, 26, "t", INK, anchor="c"); text(c, "1 × Professor's respect", 350, 124, 46, "b", INK, anchor="c")
                text(c, "(prize budget: Rs 0)", 350, 184, 34, "s", "#7a2313", prog(t, cue(51) + (cend(51) - cue(51)) * 0.62, 0.2), "c"); c.restore()
        host_corner(c, t, f, look=(-0.8, -0.2), brow=0.4 if t < cue(50) else -0.3, wing=1.0 if cue(50) < t < cend(50) else 0, prop="glass" if t < cue(50) else "chai")
        o = prog(t, end - 0.3, 0.3)
        if o > 0: c.drawRect(skia.Rect.MakeWH(W, H), P("#000000", o))
    else:
        office(c, t)
        wv = 1.0 if cue(52) < t < cue(52) + 1.6 else 0
        owl(c, 620, 855, 0.98, t, f, look=(0.2, 0), brow=0.4 * prog(t, cue(53), 0.2), wing=wv, prop=None if wv else "glass"); desk(c)
        a = prog(t, cue(52) + 0.2, 0.4); text(c, "THE OWL FILES", 1320, 430, 70, "b", MUST, a, "c"); text(c, "Stay curious.", 1320, 520, 56, "s", PAPER, prog(t, cue(52) + 1.8, 0.3), "c"); text(c, "Never trust a forward.", 1320, 592, 56, "s", PAPER, prog(t, cue(52) + 3.0, 0.3), "c")
        stamp(c, "CASE STILL OPEN", 1320, 730, 78, t, cue(53) + (cend(53) - cue(53)) * 0.5, rot=-6)
        a = prog(t, cend(53) + 0.6, 0.5); text(c, "Source: Harney et al., “Ancient DNA from the skeletons of Roopkund Lake”, Nature Communications (2019)", W / 2, 1040, 24, "r", PAPER, a * 0.8, "c")
        fade_in(c, t, end, 0.3)
        o = prog(t, TOTAL - 0.7, 0.6)
        if o > 0: c.drawRect(skia.Rect.MakeWH(W, H), P("#000000", o))

SCENES = [s0, s1, s2, s3, s4, s5, s6, s7]
def frame(f):
    t = f / FPS; si = max(k for k in SC if SC[k] <= t + 1e-6)
    arr = np.zeros((H, W, 4), np.uint8); surf = skia.Surface(arr); c = surf.getCanvas(); c.clear(col("#000000"))
    SCENES[si](c, t, f); overlay(c, f)
    end_scene = t >= cue(52) - 0.5
    if not (si == 0 and t >= TITLE_AT - 0.1) : caption(c, t)
    surf.flushAndSubmit(); return arr

if __name__ == "__main__":
    if sys.argv[1] == "still":
        from PIL import Image
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))[..., :3]).save(f"still_{float(ts):06.1f}.jpg", quality=88)
    else:
        si = int(sys.argv[1]); a = round(SC[si] * FPS); b = round(SC[si + 1] * FPS) if si + 1 in SC else round(TOTAL * FPS)
        tmp = f"sc{si}.tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for f in range(a, b): p.stdin.write(frame(f).tobytes())
        p.stdin.close()
        if p.wait() == 0: os.rename(tmp, f"sc{si}.mp4"); print("done", si, b - a)
