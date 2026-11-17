# Raat Files host: Inspector Raat, a fruit-bat detective.
# This is NOT a standalone script -- paste it into a copy of owlfiles/render.py,
# in place of the owl() function and the NIGHT/PAPER/MUST/RED/TEAL/INK/CORK palette
# line, right after the generic engine helpers (col, P, text, rrect, poly, grad_rect)
# which this reuses as-is. Keep caption(), overlay() and the portrait W,H=1080,1920
# from owlfiles/render.py unchanged.

# ---------- Raat Files palette (deep indigo night instead of Owl Files' night-blue/paper)
NIGHT, NIGHT2, SILVER, FOG, MOON, LANT, BLOOD, BONE = (
    "#120c26", "#1d1440", "#c9d2e8", "#5c6b86", "#e8e6f0", "#f0a33c", "#b23a48", "#ece3d2")
# Use these in place of Owl Files' NIGHT/PAPER/MUST/RED/TEAL/INK: BONE ~ PAPER (card/paper
# tone), LANT ~ MUST (warm accent, now a lantern glow instead of a rubber stamp), BLOOD ~ RED
# (used sparingly -- a cracked photo corner, a warning stamp -- never gore), SILVER/FOG are
# new (moonlight text, distant fog/mountains), NIGHT2 is a secondary background wash.

# ---------- the host: Inspector Raat
def bat(c, x, y, s, t, f, look=(0.15, -0.1), wing=0.0, talk=None, prop=None, tilt=0.0):
    e = ENV[min(f, len(ENV) - 1)] if talk is None else talk
    e = 0.6 * e + 0.4 * ENV[max(0, min(f - 1, len(ENV) - 1))] if talk is None else e
    bob = math.sin(t * 1.6) * 4 + e * 5
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-160, -14, 160, 20), P("#000000", 0.35, blur=14))
    c.rotate(tilt); c.translate(0, -bob)
    FUR, FUR2, EAR, CLOAK, CLOAK2 = "#5b5470", "#443f5c", "#3d3755", "#241a3e", "#160f2b"
    # cloak (reads as folded wings/cape from a distance)
    poly(c, [(-150, -60), (-210, -260), (-40, -210), (0, -230), (40, -210), (210, -260), (150, -60)], P(CLOAK))
    for k in range(5):
        xx = -170 + k * 85
        poly(c, [(xx, -70), (xx + 42, -210), (xx + 84, -70)], P(CLOAK2, 0.5))
    # feet
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            c.drawOval(skia.Rect.MakeXYWH(sx * 50 + k * 15 - 9, -14, 18, 26), P(EAR))
    # body
    c.drawOval(skia.Rect.MakeLTRB(-118, -300, 118, 0), P(FUR))
    c.drawOval(skia.Rect.MakeLTRB(-72, -230, 72, -10), P("#7a7390"))
    # wings (membrane; wing=0..1 spreads them for a dramatic beat, e.g. a jump-scare line)
    for sx in (-1, 1):
        c.save(); c.translate(sx * 95, -220); c.rotate(sx * (18 + wing * 55 + math.sin(t * 7) * 4 * wing))
        wp = skia.Path(); wp.moveTo(0, 0)
        wp.cubicTo(sx * 90, -40, sx * 230, -10, sx * 260, 90)
        wp.cubicTo(sx * 190, 40, sx * 150, 10, sx * 100, 60)
        wp.cubicTo(sx * 80, 10, sx * 40, 10, 0, 40)
        wp.close()
        c.drawPath(wp, P(FUR2, 0.96))
        for fi in range(3):
            fx = sx * (90 + fi * 55)
            c.drawLine(0, 0, fx, 10 + fi * 28, P(NIGHT, 0.5, stroke=4))
        c.restore()
    # head + big ears
    c.drawOval(skia.Rect.MakeLTRB(-120, -430, 120, -210), P(FUR))
    for sx in (-1, 1):
        c.save(); c.translate(sx * 78, -400); c.rotate(sx * 8)
        poly(c, [(-34, 0), (-20, -118), (34, -30)], P(EAR))
        poly(c, [(-20, -14), (-12, -92), (22, -28)], P("#8178a0", 0.8))
        c.restore()
    # eyes (big, round, curious-but-nervous; look param steers gaze like owl()'s)
    bl = (t * 0.23 + 0.4) % 1.0; lid = 1.0 if bl > 0.975 else 0.0
    for sx in (-1, 1):
        ex = sx * 48; ey = -320
        c.drawCircle(ex, ey, 40, P("#ffffff"))
        if lid < 0.5:
            px = ex + look[0] * 14; py = ey + look[1] * 12
            c.drawCircle(px, py, 23, P("#2a2140")); c.drawCircle(px + 7, py - 8, 7, P("#ffffff"))
        else:
            c.drawLine(ex - 30, ey + 4, ex + 30, ey + 4, P(EAR, stroke=6))
        c.drawCircle(ex, ey, 44, P(NIGHT, stroke=7))
    poly(c, [(-18, -270), (18, -270), (0, -244)], P(EAR))  # muzzle
    # beak-less mouth: a small opening that grows with voice level, plus two tiny fangs
    op = e * 10
    if op > 1:
        c.drawOval(skia.Rect.MakeLTRB(-10, -248, 10, -248 + op), P("#2a2140"))
    c.drawLine(-8, -246, -8, -236, P(BONE, stroke=5)); c.drawLine(8, -246, 8, -236, P(BONE, stroke=5))
    # round, slightly crooked spectacles (one lens cracked -- running visual gag)
    c.save(); c.rotate(-4)
    c.drawCircle(-48, -322, 46, P(NIGHT, 1, stroke=7)); c.drawCircle(48, -320, 46, P(NIGHT, 1, stroke=7))
    c.drawLine(-2, -322, 2, -320, P(NIGHT, stroke=6))
    c.drawLine(32, -340, 58, -304, P(NIGHT, 0.6, stroke=3)); c.drawLine(48, -344, 40, -300, P(NIGHT, 0.5, stroke=2))
    c.restore()
    # prop: lantern (default) or an old case notebook
    if prop != "notebook":
        c.save(); c.translate(140, -140); c.rotate(-10)
        rrect(c, -22, -10, 44, 60, 6, P("#caa24a")); rrect(c, -16, -4, 32, 44, 4, P(LANT, 0.85))
        c.drawCircle(0, 14, 26, P(LANT, 0.5, blur=18))
        c.drawLine(-22, -10, -30, -34, P("#8a6a2a", stroke=5)); c.drawLine(22, -10, 30, -34, P("#8a6a2a", stroke=5))
        c.drawLine(-30, -34, 30, -34, P("#8a6a2a", stroke=5))
        c.restore()
    else:
        c.save(); c.translate(130, -120); c.rotate(-8)
        rrect(c, -40, -28, 80, 56, 4, P(BONE)); c.drawLine(-28, -14, 28, -14, P(NIGHT, 0.5, stroke=3))
        c.drawLine(-28, 0, 28, 0, P(NIGHT, 0.5, stroke=3)); c.drawLine(-28, 14, 10, 14, P(NIGHT, 0.5, stroke=3))
        c.restore()
    c.restore()

def host_corner_raat(c, t, f, look=(0.15, -0.1), wing=0.0, prop="lantern"):
    bat(c, 970, 1840, 0.5, t, f, look=look, wing=wing, prop=prop)
