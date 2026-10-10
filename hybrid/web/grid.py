"""Draw a labelled coordinate grid over the brass background so window positions can be read off
by eye and then verified by drawing candidate boxes back on top.

Deliberately simple: segmentation on a photoreal AI render merges dark glass, shadows and the black
field into one blob, so eyeball-and-verify beats thresholding here.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "BrassBackground.png")
im = Image.open(SRC).convert("RGB")
W, H = im.size

ov = im.copy()
d = ImageDraw.Draw(ov)
try:
    f = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 15)
except Exception:
    f = ImageFont.load_default()

MAJOR, MINOR = 100, 50
for x in range(0, W, MINOR):
    major = x % MAJOR == 0
    d.line([x, 0, x, H], fill=(255, 0, 0) if major else (90, 40, 40), width=2 if major else 1)
    if major:
        d.text((x + 3, 3), str(x), font=f, fill=(255, 255, 0))
        d.text((x + 3, H - 22), str(x), font=f, fill=(255, 255, 0))
for y in range(0, H, MINOR):
    major = y % MAJOR == 0
    d.line([0, y, W, y], fill=(0, 130, 255) if major else (35, 55, 90), width=2 if major else 1)
    if major:
        d.text((3, y + 3), str(y), font=f, fill=(255, 255, 0))
        d.text((W - 46, y + 3), str(y), font=f, fill=(255, 255, 0))

ov.save(os.path.join(HERE, "grid_overlay.png"))
print("grid_overlay.png", ov.size, "— 50 px minors, 100 px labelled majors")
