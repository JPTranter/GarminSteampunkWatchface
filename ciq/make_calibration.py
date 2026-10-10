"""Build a hue-calibration background for checking the AMOLED colour correction ON THE WATCH.

The correction in device_colour.py was estimated from one phone photo. This writes a background
split into four vertical strips of the real face, each pre-corrected by a different hue shift,
with the shift printed at the top of the strip:

    0 deg (uncorrected) | +6 deg | +11 deg (the measured default) | +16 deg

Sideload a build of it, look at the watch in normal light, and pick the strip whose brass looks
like brass (not copper, not green-yellow). Then set HUE_SHIFT_DEG in device_colour.py to it.

Usage:
    python make_calibration.py     # writes artwork/calib_hue.png
Then build it as a separate .prg without touching the shipping background:
    python make_calibration.py --install   # copies it over resources/drawables/background.png
    (build + push_watch.ps1), then:  python prepare_resources.py   # restores the shipping one
"""
import argparse
import os
import shutil

from PIL import Image, ImageDraw

import device_colour

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "artwork", "cand_split.png")
OUT = os.path.join(HERE, "artwork", "calib_hue.png")
SHIFTS = [0, 6, 11, 16]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true",
                    help="copy over resources/drawables/background.png for a calibration build")
    args = ap.parse_args()

    base = Image.open(SRC).convert("RGB")
    out = base.copy()
    sw = base.width // len(SHIFTS)
    d = ImageDraw.Draw(out)
    for i, shift in enumerate(SHIFTS):
        strip = device_colour.correct(base, hue_shift_deg=shift)
        box = (i * sw, 0, (i + 1) * sw, base.height)
        out.paste(strip.crop(box), box[:2])
        if i:
            d.line((i * sw, 0, i * sw, base.height), fill=(255, 255, 255))
        d.rectangle((i * sw + 2, 2, i * sw + 34, 14), fill=(0, 0, 0))
        d.text((i * sw + 5, 3), f"+{shift}", fill=(255, 255, 255))
    out.save(OUT)
    print("wrote", OUT, "strips:", ", ".join(f"+{s} deg" for s in SHIFTS))
    if args.install:
        dst = os.path.join(HERE, "resources", "drawables", "background.png")
        shutil.copyfile(OUT, dst)
        print("installed over", dst, "- run prepare_resources.py afterwards to restore")
