"""Cinematic layer for Owl Files / Raat Files Shorts (added 17 Nov 2026).

Turns AI-generated still "plates" (stylized 3D animated-film look) into moving,
film-like shots: eased camera moves, parallax fog, drifting particles, light
flicker, light shafts, colour grade, vignette and grain. Every shot moves;
nothing on screen should sit still for more than ~1.5 s.

Usage inside render.py (1080x1920, 30 fps):

    from cine import Plate, Shot, film_finish
    room = Plate("assets/env_room.jpg")             # watermark strip cropped, upscaled
    shot = Shot(room, move="push", focus=(0.5, 0.6), fog="#7fa6c9", dust=40,
                flicker=0.25, shafts=True, grade="moon")
    rgb = shot.frame(t_local, dur)                    # HxWx3 uint8, no grain yet
    ... draw host / captions / labels with skia on top ...
    rgb = film_finish(rgb, f)                        # grain + vignette, last step

Moves: push (slow zoom in), pull, pan_l, pan_r, tilt_up, tilt_down, drift.
Grades: moon (teal/blue night), lamp (amber), sepia (archive), cold, warm, none.
"""
import math
import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30
_rng = np.random.default_rng(7)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


class Plate:
    """An AI still prepared for camera moves: crops the free-mode watermark strip,
    upscales with Lanczos + light unsharp mask to 1.25x the frame (room to move)."""

    def __init__(self, path, crop_bottom=0.055, scale=1.25):
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        if im is None:
            raise FileNotFoundError(path)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        h, w = im.shape[:2]
        im = im[: int(h * (1 - crop_bottom))]
        h, w = im.shape[:2]
        tw, th = int(W * scale), int(H * scale)
        r = max(tw / w, th / h)
        im = cv2.resize(im, (int(w * r + 0.5), int(h * r + 0.5)), interpolation=cv2.INTER_LANCZOS4)
        h, w = im.shape[:2]
        y0, x0 = (h - th) // 2, (w - tw) // 2
        im = im[y0:y0 + th, x0:x0 + tw]
        blur = cv2.GaussianBlur(im, (0, 0), 2.0)
        self.img = cv2.addWeighted(im, 1.45, blur, -0.45, 0)
        self.h, self.w = self.img.shape[:2]


def _camera(plate, move, p, focus):
    """Return the frame cut from the plate for progress p (0..1)."""
    e = ease(p)
    fx, fy = focus
    z0, z1 = 1.0, 1.0
    dx = dy = 0.0
    if move == "push":
        z0, z1 = 1.0, 1.18
    elif move == "pull":
        z0, z1 = 1.18, 1.0
    elif move == "pan_l":
        dx = 0.5 - e
    elif move == "pan_r":
        dx = e - 0.5
    elif move == "tilt_up":
        dy = 0.5 - e
    elif move == "tilt_down":
        dy = e - 0.5
    else:  # drift: gentle push + sideways float
        z0, z1 = 1.04, 1.12
        dx = 0.25 * math.sin(p * math.pi)
    z = z0 + (z1 - z0) * e
    cw, ch = plate.w / 1.25 / z, plate.h / 1.25 / z
    spare_x, spare_y = plate.w - cw, plate.h - ch
    cx = fx * plate.w + dx * spare_x * 0.8
    cy = fy * plate.h + dy * spare_y * 0.8
    x0 = min(max(cx - cw / 2, 0), plate.w - cw)
    y0 = min(max(cy - ch / 2, 0), plate.h - ch)
    M = np.float32([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]])
    return cv2.warpAffine(plate.img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# --- shared noise textures (built once) ---------------------------------------
def _fog_tex(seed):
    r = np.random.default_rng(seed)
    acc = np.zeros((H // 4, W // 2), np.float32)
    for k, s in enumerate((6, 12, 24, 48)):
        n = r.random((max(2, H // 4 // s), max(2, W // 2 // s))).astype(np.float32)
        acc += cv2.resize(n, (W // 2, H // 4), interpolation=cv2.INTER_CUBIC) / (k + 1)
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return np.tile(acc, (1, 2))  # wide strip so it can scroll sideways


_FOG = [_fog_tex(1), _fog_tex(2)]
_GRAIN = [(_rng.standard_normal((H // 2, W // 2)) * 9).astype(np.float32) for _ in range(6)]
_VIG = None


def _vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _VIG = np.clip(1.08 - 0.55 * d ** 2.2, 0.35, 1.0)[..., None]
    return _VIG


GRADES = {
    "moon": ((0.86, 0.98, 1.12), (6, 12, 26)),
    "lamp": ((1.12, 0.98, 0.80), (18, 8, 0)),
    "sepia": ((1.08, 0.96, 0.78), (14, 8, 0)),
    "cold": ((0.90, 1.00, 1.10), (0, 6, 14)),
    "warm": ((1.08, 1.0, 0.9), (10, 4, 0)),
    "none": ((1, 1, 1), (0, 0, 0)),
}


class Shot:
    def __init__(self, plate, move="push", focus=(0.5, 0.5), fog=None, fog_amt=0.35,
                 dust=0, dust_col="#fff1c9", flicker=0.0, shafts=False, grade="moon",
                 lightning=(), seed=0):
        self.p, self.move, self.focus = plate, move, focus
        self.fog = hexrgb(fog) if fog else None
        self.fog_amt, self.flicker, self.shafts = fog_amt, flicker, shafts
        self.grade = GRADES[grade]
        self.lightning = lightning  # local times of lightning flashes
        r = np.random.default_rng(seed + 99)
        self.dust = np.c_[r.random(dust) * W, r.random(dust) * H, r.random(dust) * 0.9 + 0.3,
                          r.random(dust) * 6.28]
        self.dust_col = tuple(int(c) for c in hexrgb(dust_col))

    def frame(self, t, dur):
        img = _camera(self.p, self.move, t / max(dur, 1e-6), self.focus).astype(np.float32)
        # light flicker (lantern / bulb), smooth noise
        if self.flicker:
            f = 1 + self.flicker * (0.5 * math.sin(t * 13.1) + 0.3 * math.sin(t * 29.7 + 1) +
                                    0.2 * math.sin(t * 3.3)) * 0.35
            img *= f
        # god-ray shafts from the upper-left
        if self.shafts:
            yy, xx = np.mgrid[0:H:8, 0:W:8].astype(np.float32)
            a = np.sin((xx * 0.8 + yy * 0.45) / 55 + t * 0.4) * 0.5 + 0.5
            m = cv2.resize((a ** 6) * np.clip(1 - yy / H, 0, 1), (W, H))
            img += m[..., None] * 38
        # parallax fog: two layers scrolling at different speeds
        if self.fog is not None:
            acc = np.zeros((H // 4, W // 2), np.float32)
            for k, tex in enumerate(_FOG):
                off = int((t * (14 + 22 * k)) % (W // 2))
                acc += tex[:, off:off + W // 2] * (0.6 if k else 0.4)
            fogm = cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)
            fogm *= np.linspace(0.55, 1.0, H, dtype=np.float32)[:, None]
            a = (fogm * self.fog_amt)[..., None]
            img = img * (1 - a) + self.fog * a
        # lightning
        for lt in self.lightning:
            d = t - lt
            if 0 <= d < 0.35:
                img += 120 * (math.exp(-d * 14) + 0.5 * math.exp(-max(d - 0.12, 0) * 20) * (d > 0.12))
        # grade
        mul, add = self.grade
        img = img * np.array(mul, np.float32) + np.array(add, np.float32)
        out = np.clip(img, 0, 255).astype(np.uint8)
        # floating dust / embers
        if len(self.dust):
            for x, y, s, ph in self.dust:
                px = int((x + 18 * math.sin(t * 0.6 + ph) + t * 6 * s) % W)
                py = int((y - t * 22 * s) % H)
                tw = 0.55 + 0.45 * math.sin(t * 2.3 + ph * 3)
                c = tuple(int(v * tw) for v in self.dust_col)
                cv2.circle(out, (px, py), max(1, int(2.6 * s)), c, -1, cv2.LINE_AA)
        return out


def crossfade(a, b, k):
    return cv2.addWeighted(a, 1 - k, b, k, 0)


def whip(a, b, k, direction=1):
    """Whip-pan transition: motion-blur smear from shot a into shot b, k in 0..1."""
    src = a if k < 0.5 else b
    amt = 1 - abs(k - 0.5) * 2
    shift = int(direction * (k - 0.5) * W * 0.9)
    m = np.float32([[1, 0, shift], [0, 1, 0]])
    s = cv2.warpAffine(src, m, (W, H), borderMode=cv2.BORDER_REFLECT)
    ks = max(1, int(amt * 90)) | 1
    return cv2.blur(s, (ks, 1))


def film_finish(rgb, f):
    """Grain + vignette. Apply last, after captions, so everything sits in the same 'film'."""
    img = rgb.astype(np.float32) * _vignette()
    g = cv2.resize(_GRAIN[f % len(_GRAIN)], (W, H), interpolation=cv2.INTER_NEAREST)
    img += g[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)
