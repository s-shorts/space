"""Depth maps (Depth-Anything-V2 small) for every image, used for 2.5D parallax camera moves."""
import glob, os
from PIL import Image
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=-1)
os.makedirs("out/depth", exist_ok=True)
for f in sorted(glob.glob("out/ai/*.jpg") + glob.glob("out/ai/*.png") + glob.glob("out/photos/*.jpg") + glob.glob("out/photos/*.png")):
    try:
        im = Image.open(f).convert("RGB"); im.thumbnail((1280, 1280))
        d = pipe(im)["depth"]; d.save("out/depth/" + os.path.splitext(os.path.basename(f))[0] + ".png"); print("depth", f, flush=True)
    except Exception as e:
        print("depth fail", f, e)
