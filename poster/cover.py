#!/usr/bin/env python3
"""Make a cover image (Instagram Reel thumbnail) for a vertical video.

Picks the most detailed, well-lit frame from the first 60% of the video (so
the cover is never a black fade-in), blurs and darkens it, and writes the title
across the middle in large type. The middle 1080x1440 stays readable in the
Instagram profile grid, which crops Reels to 3:4.

    python3 poster/cover.py VIDEO.mp4 "Title" cover.jpg
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FONT_DIRS = ["/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(video)], capture_output=True, text=True)
    return float(out.stdout.strip() or 0)


def best_frame(video, tmp):
    from PIL import Image, ImageStat
    dur = duration(video) or 10
    best, best_score = None, -1
    for i in range(12):
        t = 1.0 + (dur * 0.6 - 1.0) * i / 11
        path = Path(tmp) / f"f{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                        "-frames:v", "1", "-q:v", "2", str(path)], check=False)
        if not path.is_file():
            continue
        img = Image.open(path).convert("RGB")
        st = ImageStat.Stat(img.convert("L"))
        mean, std = st.mean[0], st.stddev[0]
        score = std + min(mean, 110) * 0.5   # detail first, then brightness
        if mean > 18 and score > best_score:
            best, best_score = img.copy(), score
    if best is None:
        raise RuntimeError("no usable frame")
    return best


def font(size):
    from PIL import ImageFont
    for f in FONT_DIRS:
        if Path(f).is_file():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def make_cover(video, title, out):
    from PIL import Image, ImageDraw, ImageFilter
    title = re.sub(r"#\w+", "", title).strip(" -|")
    with tempfile.TemporaryDirectory() as tmp:
        img = best_frame(video, tmp).resize((1080, 1920))
    W, H = img.size
    # blur the frame so its own captions and headlines don't fight the title,
    # then darken it, most of all behind the text
    from PIL import ImageEnhance
    img = img.filter(ImageFilter.GaussianBlur(16))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.25)).enhance(1.3)
    shade = Image.new("L", (W, H), 90)
    d = ImageDraw.Draw(shade)
    d.rectangle((0, int(H * 0.34), W, int(H * 0.68)), fill=170)
    shade = shade.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shade)

    draw = ImageDraw.Draw(img)
    size = 120
    while size > 60:
        fnt = font(size)
        lines = wrap(draw, title.upper(), fnt, W - 140)
        if len(lines) <= 4:
            break
        size -= 8
    lh = int(size * 1.18)
    y = int(H * 0.51 - lh * len(lines) / 2)
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=fnt)
        colour = (255, 205, 70) if i == len(lines) - 1 and len(lines) > 1 else (255, 255, 255)
        draw.text(((W - w) / 2, y), line, font=fnt, fill=colour,
                  stroke_width=max(4, size // 14), stroke_fill=(0, 0, 0))
        y += lh
    img.save(out, quality=90)
    return out


if __name__ == "__main__":
    make_cover(sys.argv[1], sys.argv[2], sys.argv[3])
    print(sys.argv[3])
