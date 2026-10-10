"""Verify the corrected layout: dial-face circles at their MEASURED centres, plus sample text in the
new positions and styles (raised + stretched tube digits, no comma in the steps, raised HR, date
centred on the measured right-dial face).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "BrassBackground.png")).convert("RGB")
ov = im.copy()
d = ImageDraw.Draw(ov)
SERIF = r"C:\Windows\Fonts\georgiab.ttf"


def f(px):
    return ImageFont.truetype(SERIF, px)


# measured dial-face centres (from the constricted dark-face scans)
L_C, L_R = (209, 605), 110
R_C, R_R = (813, 657), 110
for (cx, cy), r, col in ((L_C, L_R, (0, 255, 90)), (R_C, R_R, (0, 255, 90))):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    d.line([cx - 14, cy, cx + 14, cy], fill=(255, 60, 60), width=2)
    d.line([cx, cy - 14, cx, cy + 14], fill=(255, 60, 60), width=2)

# ---- proposed TUBE digits: raised, and taller/thinner (drawn stretched to preview the CSS scale)
TUBE_CX = [272, 439, 591, 747]
TUBE_CY = 258
for cx in TUBE_CX:
    d.rectangle([cx - 60, TUBE_CY - 85, cx + 60, TUBE_CY + 85], outline=(0, 255, 90), width=1)
for cx, ch in zip(TUBE_CX, "1009"):
    tmp = Image.new("RGB", (200, 240), (0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((100, 120), ch, font=f(120), fill=(240, 248, 255), anchor="mm")
    tmp = tmp.resize((int(200 * 0.74), int(240 * 1.34)), Image.LANCZOS)  # scaleX .74, scaleY 1.34
    ov.paste(tmp, (cx - tmp.width // 2, TUBE_CY - tmp.height // 2), None)

# ---- proposed STEPS: no comma, right-aligned on drums 2..5
for cx, ch in zip([446, 504, 562, 619], "8342"):
    d.text((cx, 615), ch, font=f(68), fill=(255, 246, 220), anchor="mm")

# ---- proposed HR + date on the measured faces
d.text((L_C[0], 664), "72", font=f(72), fill=(255, 246, 220), anchor="mm")
d.text((L_C[0], 636), "BPM", font=f(20), fill=(255, 216, 160), anchor="mm")
d.text((R_C[0], 600), "WED", font=f(30), fill=(255, 216, 160), anchor="mm")
d.text((R_C[0], 657), "30", font=f(72), fill=(255, 246, 220), anchor="mm")
d.text((R_C[0], 700), "SEP", font=f(20), fill=(255, 216, 160), anchor="mm")

ov.save(os.path.join(HERE, "placement_check2.png"))
print("placement_check2.png written")
