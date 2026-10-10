"""Build a hue-calibration background for checking the AMOLED colour correction ON THE WATCH.

The correction in device_colour.py was estimated from one phone photo, and a later photo of the watch
beside the monitor showed a residual: the mid brass matches (hue 28.2 on both) but the brightest and
darkest warm tones come out 3-4 deg yellower and 0.1-0.2 more saturated on the panel. So the shift is
worth re-picking by eye.

Each band is the SAME piece of the face, pre-corrected by a different hue shift, stacked down the
screen and labelled - the same content repeated rather than four slices of one frame, so the bands can
be compared like for like (a slice-wise layout compares different hardware in each strip):

    +4 deg | +8 deg | +11 deg (the shipped default) | +14 deg

Sideload a build of it, look at the watch in normal light, and pick the band whose brass looks like
brass (not copper, not green-yellow). Then set HUE_SHIFT_DEG in device_colour.py to that value and
re-run `python make.py assets` - the baked art AND the live ink both take the shift from there.

Usage:
    python make_calibration.py               # writes artwork/calib_hue.png
    python make_calibration.py --install     # also copies it over resources/drawables/background.png
Then: python make.py build && python make.py push
and afterwards: python prepare_resources.py     # restore the shipping background
"""
import argparse
import os
import shutil

from PIL import Image, ImageDraw

import device_colour

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "artwork", "cand_split.png")
OUT = os.path.join(HERE, "artwork", "calib_hue.png")
SHIFTS = [4, 8, 11, 14]
BAND = (96, 196)        # the screen rows to repeat: the collars and manifold, brass-rich
LABEL_H = 12

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true",
                    help="copy over resources/drawables/background.png for a calibration build")
    args = ap.parse_args()

    base = Image.open(SRC).convert("RGB")
    w, h = base.size
    y0, y1 = BAND
    step = h // len(SHIFTS)
    out = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(out)
    for i, shift in enumerate(SHIFTS):
        # the whole frame corrected at this shift, then the SAME band lifted out of it
        corr = device_colour.correct(base, hue_shift_deg=shift)
        out.paste(corr.crop((0, y0, w, y1)), (0, i * step))
        d.rectangle((0, i * step, 54, i * step + LABEL_H), fill=(0, 0, 0))
        d.text((3, i * step + 2), f"+{shift} deg", fill=(255, 255, 255))
    out.save(OUT)
    print("wrote", OUT, "bands:", ", ".join(f"+{s} deg" for s in SHIFTS))
    if args.install:
        dst = os.path.join(HERE, "resources", "drawables", "background.png")
        shutil.copyfile(OUT, dst)
        print("installed over", dst, "- run prepare_resources.py afterwards to restore")
