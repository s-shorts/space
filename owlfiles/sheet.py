import sys, glob
from PIL import Image
fs=sorted(glob.glob("still_*.jpg")); n=len(fs); cols=2; rows=(n+1)//2
S=Image.new("RGB",(1920,540*rows))
for i,f in enumerate(fs): S.paste(Image.open(f).resize((960,540)),((i%2)*960,(i//2)*540))
S.save(sys.argv[1],quality=85)
