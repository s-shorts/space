"""Correct Hindi (Devanagari) text for skia scenes -- added 21 Nov 2026.

skia-python's drawString/drawSimpleText does NOT shape Devanagari: vowel signs and
conjuncts come out wrong (e.g. "किला" renders as "कलि"). Always draw Hindi through
these helpers, which shape with Pillow + libraqm and blit the result as a skia image.

    from hindi_text import hi_text, hi_wrap, hi_caption
    hi_text(c, "भानगढ़ का किला", x=540, y=400, size=72, color="#ffffff", align="center")
    hi_caption(c, "सूरज ढलने के बाद यहाँ आना मना है।", alpha=1.0)   # bottom caption box

Fonts: Poppins (Bold/Medium/Regular, in /usr/share/fonts/truetype/google-fonts/) covers
Devanagari and Latin, so mixed lines like "1977 में Enfield" work. Numbers stay as
digits (1977, 45 घंटे) on screen even though the voice says them as words.
"""
import functools
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/google-fonts/"
WEIGHTS = {"bold": "Poppins-Bold.ttf", "medium": "Poppins-Medium.ttf", "regular": "Poppins-Regular.ttf"}


@functools.lru_cache(maxsize=64)
def _font(size, weight):
    return ImageFont.truetype(FONT_DIR + WEIGHTS[weight], int(size), layout_engine=ImageFont.Layout.RAQM)


def _rgba(color, alpha):
    if isinstance(color, str):
        h = color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    else:
        r, g, b = color[:3]
    return (r, g, b, int(255 * max(0.0, min(1.0, alpha))))


def text_width(s, size, weight="bold"):
    return _font(size, weight).getlength(s, language="hi")


def hi_wrap(s, size, max_w, weight="bold"):
    """Greedy word wrap measured with the shaped width."""
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if cur and text_width(t, size, weight) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


@functools.lru_cache(maxsize=512)
def _render(s, size, weight, rgba, stroke, stroke_rgba):
    f = _font(size, weight)
    l, t, r, b = f.getbbox(s, language="hi", stroke_width=stroke)
    pad = stroke + 4
    im = Image.new("RGBA", (int(r - l) + 2 * pad, int(b - t) + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=rgba, language="hi",
                            stroke_width=stroke, stroke_fill=stroke_rgba)
    arr = np.ascontiguousarray(np.array(im))
    return skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType), pad, t


def hi_text(c, s, x, y, size=56, color="#ffffff", alpha=1.0, weight="bold",
            align="left", stroke=0, stroke_color="#000000"):
    """Draw one line. (x, y) is the left/centre/right point of the text's top edge."""
    if not s or alpha <= 0:
        return 0
    img, pad, top = _render(s, int(size), weight, _rgba(color, 1.0), int(stroke), _rgba(stroke_color, 1.0))
    w = img.width() - 2 * pad
    x0 = x if align == "left" else (x - w / 2 if align == "center" else x - w)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(max(0.0, min(1.0, alpha)))
    c.drawImage(img, x0 - pad, y - pad + top, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    return w


def hi_lines(c, s, x, y, size, max_w, line_h=None, **kw):
    """Wrapped paragraph; returns the y just below the last line."""
    line_h = line_h or size * 1.45
    for ln in hi_wrap(s, size, max_w, kw.get("weight", "bold")):
        hi_text(c, ln, x, y, size, **kw)
        y += line_h
    return y


def hi_caption(c, s, alpha=1.0, cx=540, y=1525, size=50, max_w=900,
               box="#000000", box_alpha=0.55, color="#ffffff"):
    """Bottom-of-screen caption box for portrait Shorts (same spot as render.py's caption)."""
    lines = hi_wrap(s, size, max_w)
    lh = size * 1.5
    w = max(text_width(l, size) for l in lines) + 60
    h = lh * len(lines) + 30
    p = skia.Paint(AntiAlias=True, Color=skia.Color(*_rgba(box, 1.0)[:3]))
    p.setAlphaf(box_alpha * alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(cx - w / 2, y - 15, w, h), 22, 22, p)
    yy = y
    for ln in lines:
        hi_text(c, ln, cx, yy, size, color=color, alpha=alpha, align="center")
        yy += lh
