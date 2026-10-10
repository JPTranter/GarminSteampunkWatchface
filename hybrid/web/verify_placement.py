"""Verify candidate placements by DRAWING the actual text into the measured boxes.

If the digits land inside the windows in the overlay, the coordinates are right. This is the
verification step for the HTML model built afterwards.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "BrassBackground.png")).convert("RGB")
W, H = im.size
ov = im.copy()
d = ImageDraw.Draw(ov)

SERIF = r"C:\Windows\Fonts\georgiab.ttf"


def fnt(px):
    return ImageFont.truetype(SERIF, px)


# candidate boxes: (x0, y0, x1, y1)
TUBES = [(200, 170, 350, 375), (370, 170, 510, 375), (525, 170, 660, 375), (675, 170, 820, 375)]
CNT = (358, 548, 652, 688)
LGAUGE = (85, 525, 332, 762)          # dark dial of the left gauge
RGAUGE = (712, 525, 908, 762)         # dark dial of the right gauge

for (x0, y0, x1, y1) in TUBES:
    d.rectangle([x0, y0, x1, y1], outline=(0, 255, 90), width=2)
# counter + its five windows
d.rectangle(list(CNT), outline=(0, 255, 90), width=2)
cw = (CNT[2] - CNT[0]) / 5.0
for i in range(5):
    wx0 = CNT[0] + i * cw
    d.rectangle([wx0 + 3, CNT[1] + 5, wx0 + cw - 3, CNT[3] - 5], outline=(255, 80, 80), width=1)
d.rectangle(list(LGAUGE), outline=(0, 255, 90), width=2)
d.rectangle(list(RGAUGE), outline=(0, 255, 90), width=2)

# ---- draw sample text where it would actually go
DIG = fnt(150)
for (x0, y0, x1, y1), ch in zip(TUBES, "1009"):
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), ch, font=DIG, fill=(255, 246, 220), anchor="mm")

CD = fnt(84)
for i, ch in enumerate("8342"):
    wx0 = CNT[0] + i * cw
    # 4 digits spread over the middle 4 windows to leave a gap pattern
    d.text((wx0 + cw / 2, (CNT[1] + CNT[3]) / 2), ch, font=CD, fill=(255, 246, 220), anchor="mm")

d.text((LGAUGE[0] + (LGAUGE[2] - LGAUGE[0]) / 2, 706), "72", font=fnt(72),
       fill=(255, 246, 220), anchor="mm")
d.text((RGAUGE[0] + (RGAUGE[2] - RGAUGE[0]) / 2, 700), "30", font=fnt(72),
       fill=(255, 246, 220), anchor="mm")
d.text((RGAUGE[0] + (RGAUGE[2] - RGAUGE[0]) / 2, 578), "WED", font=fnt(30),
       fill=(255, 210, 150), anchor="mm")

ov.save(os.path.join(HERE, "placement_check.png"))
print("placement_check.png written — boxes + sample text")
