"""Candidate LARGER layouts for the face: mockups to choose between, not shipping resources.

WHY: the shipped width-fit (scale 0.3365) keeps the whole device on screen, which leaves the tubes
~210 px wide on a 320 px screen and every readout small. The user asked for the tubes to fill the
top and the dials to fill the bottom, with the dials' outer edges allowed to run off the screen.

A single uniform scale cannot do both: the dial CENTRES sit at x 207 / 813 on the 1024 grid, so
any scale above ~0.38 pushes a dial's readout off the screen edge before the tubes fill the width.
So the "split" candidates scale the TOP band (tubes + manifold) and the BOTTOM band (dials +
counter + gears) independently and join them across the dark gap under the manifold, with a short
feathered blend so the seam has no hard line.

Every text coordinate is derived from the SHIPPED coordinates mapped back to the 1024 grid through
the old transform, then forward through the candidate's transform — so the hand nudges recorded in
SteampunkNixieView.mc are kept, not lost. Fonts are scaled by the same factor as their band.

Writes ciq/artwork/zoom/<name>.png (1x) and _zoom_compare.png (2x, side by side, current first).

DECISION RECORD: the user chose C (top 0.49 / bottom 0.43). This script is kept as the record of
the comparison that was shown; the shipping implementation of C lives in prepare_artwork.py (which
also removes the heart-rate needle, as the user asked once C was chosen). The "CURRENT" panel is
read from artwork/face_preview.png, so re-running this after the change shows C as current.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "reference", "BrassBackground.png")
OUT = os.path.join(HERE, "artwork", "zoom")
os.makedirs(OUT, exist_ok=True)
W, H = 320, 360
SERIF_BD = r"C:\Windows\Fonts\timesbd.ttf"
SERIF = r"C:\Windows\Fonts\georgia.ttf"

src = Image.open(SRC).convert("RGB")
ImageDraw.Draw(src).rectangle((820, 0, 1024, 62), fill=(0, 0, 0))   # watermark
SW, SH = src.size

# ---- shipped state (old transform: screen = src*0.3365 + (-12, +31)) -> 1024 grid
OLD_S, OLD_OX, OLD_OY = 0.3365, -12, 31


def to_src(x, y):
    return (x - OLD_OX) / OLD_S, (y - OLD_OY) / OLD_S


SHIPPED = {  # name: (screen x, screen y, font, band)
    "t0": (83, 117, "time", "top"), "t1": (136, 117, "time", "top"),
    "t2": (183, 117, "time", "top"), "t3": (239, 117, "time", "top"),
    "s0": (138, 233, "step", "bot"), "s1": (158, 230, "step", "bot"),
    "s2": (177, 230, "step", "bot"), "s3": (196, 230, "step", "bot"),
    "hr": (58, 229, "mid", "bot"), "bpm": (58, 256, "label", "bot"),
    "wd": (262, 221, "label", "bot"), "day": (262, 253, "small", "bot"),
    "mon": (262, 282, "label", "bot"),
}
TEXT = {"t0": "1", "t1": "0", "t2": "0", "t3": "9", "s0": "8", "s1": "3", "s2": "4", "s3": "2",
        "hr": "72", "bpm": "BPM", "wd": "WED", "day": "30", "mon": "SEP"}
# shipped font point sizes / condense (make_fonts.py)
FONTS = {"time": (76, 0.58, SERIF_BD), "small": (48, 0.62, SERIF_BD), "mid": (43, 0.62, SERIF_BD),
         "step": (34, 0.62, SERIF_BD), "label": (16, 0.88, SERIF)}
INK = {"time": (234, 246, 255), "small": (255, 243, 216), "mid": (255, 243, 216),
       "step": (255, 243, 216), "label": (255, 216, 160)}
GLOW1, GLOW2 = (0x2F, 0x6E, 0xA8), (0x15, 0x33, 0x4F)

CX = 512          # horizontal centre of the device on the 1024 grid
SEAM = 506        # source y of the join: the dark gap between the manifold and the dial tops


class Layout:
    """Top band: screen = (src - CX)*st + 160, src_y*st + oy.  Bottom band continues from the seam."""

    def __init__(self, name, st, sb, top_y=4, sb_y_extra=0):
        self.name, self.st, self.sb = name, st, sb
        self.oy = top_y - 60 * st            # src y 60 = tip of the tube nipples
        self.seam_y = SEAM * st + self.oy + sb_y_extra

    def map(self, x, y, band):
        if band == "top":
            return (x - CX) * self.st + 160, y * self.st + self.oy
        return (x - CX) * self.sb + 160, (y - SEAM) * self.sb + self.seam_y

    def background(self):
        canvas = Image.new("RGB", (W, H), (0, 0, 0))
        for band, s in (("bot", self.sb), ("top", self.st)):
            big = src.resize((round(SW * s), round(SH * s)), Image.LANCZOS)
            ox, oy = self.map(0, 0, band)
            layer = Image.new("RGB", (W, H), (0, 0, 0))
            layer.paste(big, (round(ox), round(oy)))
            if band == "bot":
                canvas = layer
                continue
            # top band over the bottom: opaque above the seam, 8 px linear feather below it
            seam = round(self.seam_y)
            m = np.zeros((H, W), np.float32)
            m[:seam - 4] = 1.0
            for i in range(8):
                r = seam - 4 + i
                if 0 <= r < H:
                    m[r] = 1.0 - (i + 1) / 9
            mask = Image.fromarray((m * 255).astype(np.uint8), "L")
            canvas = Image.composite(layer, canvas, mask)
        return canvas


def glyph_run(text, px, condense, face):
    f = ImageFont.truetype(face, px)
    out = []
    for ch in text:
        c = Image.new("L", (px * 3, px * 3), 0)
        ImageDraw.Draw(c).text((6, 6 + px), ch, font=f, fill=255, anchor="ls")
        bb = c.getbbox()
        g = c.crop(bb)
        out.append((g.resize((max(1, round(g.width * condense)), g.height), Image.LANCZOS),
                    bb[3]))  # bottom = baseline-ish for alignment
    return out


def draw_centred(canvas, text, cx, cy, px, condense, face, colour):
    gl = glyph_run(text, px, condense, face)
    total = sum(g.width + 1 for g, _ in gl) - 1
    hgt = max(g.height for g, _ in gl)
    x = round(cx - total / 2)
    for g, _ in gl:
        y = round(cy - hgt / 2) + (hgt - g.height)       # bottom-aligned glyphs
        canvas.paste(Image.new("RGB", g.size, colour), (x, y), g)
        x += g.width + 1
    return hgt


def render(lay, glow_scale=1):
    face = lay.background()
    report = []
    k = {"top": lay.st / OLD_S, "bot": lay.sb / OLD_S}
    for key, (x, y, font, band) in SHIPPED.items():
        sx, sy = to_src(x, y)
        px, py = lay.map(sx, sy, band)
        pt, cond, ttf = FONTS[font]
        pt = round(pt * k[band])
        if font == "time":
            r2, r1 = round(2 * k[band]), max(1, round(1 * k[band]))
            for rad, col in ((r2, GLOW2), (r1, GLOW1)):
                for dx in range(-rad, rad + 1):
                    for dy in range(-rad, rad + 1):
                        if max(abs(dx), abs(dy)) == rad:
                            draw_centred(face, TEXT[key], px + dx, py + dy, pt, cond, ttf, col)
        h = draw_centred(face, TEXT[key], px, py, pt, cond, ttf, INK[font])
        report.append(f"{key}={round(px)},{round(py)} ({h}px)")
    return face, report


CANDIDATES = [
    Layout("A_uniform_038", 0.38, 0.38, top_y=4),
    Layout("B_split_046_040", 0.46, 0.40, top_y=2),
    Layout("C_split_049_043", 0.49, 0.43, top_y=0),
]

if __name__ == "__main__":
    current = Image.open(os.path.join(HERE, "artwork", "face_preview.png")).convert("RGB")
    current = current.resize((W, H), Image.LANCZOS)
    imgs = [("CURRENT (0.3365)", current)]
    for lay in CANDIDATES:
        img, rep = render(lay)
        img.save(os.path.join(OUT, lay.name + ".png"))
        print(f"{lay.name}: top {lay.st} bot {lay.sb} seam y {lay.seam_y:.0f}")
        print("   " + "  ".join(rep))
        imgs.append((f"{lay.name}  top x{lay.st / OLD_S:.2f} / bottom x{lay.sb / OLD_S:.2f}", img))
    pad = 16
    sheet = Image.new("RGB", (len(imgs) * (W * 2 + pad) + pad, H * 2 + 34), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (lab, im) in enumerate(imgs):
        x = pad + i * (W * 2 + pad)
        sheet.paste(im.resize((W * 2, H * 2), Image.LANCZOS), (x, 28))
        d.text((x, 8), lab, fill=(255, 220, 120))
    p = os.path.join(OUT, "_zoom_compare.png")
    sheet.save(p)
    print("wrote", p)
