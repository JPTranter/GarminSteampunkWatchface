"""Prepare Connect IQ resources: the shipping background and the launcher icon.

Pipeline: artwork/cand_split.png (prepare_artwork.py)
          -> device_colour.correct()   pre-compensate the AMOLED's red shift on warm tones
          -> resources/drawables/background.png   (FULL colour, 24-bit PNG)

Why full colour, not a palette PNG: the resource compiler does its own colour reduction. Garmin's
Resources page: `automaticPalette` "Automatically determine a reduced color palette ... Images will
be limited to 256 colors for 16-bit color devices" and it defaults to TRUE on them. Measured: a
64-colour, a 256-colour and a full-colour PNG compiled to .prg files within 0.4 % of each other
(221,804 / 222,156 / 222,684 B). So reducing to 64 colours here only threw away colours the
compiler would have kept: it was the posterised tube glass. drawables.xml decides the on-device
depth (see the comment there); this script always hands the compiler the full-quality frame.

The old 0.3365 note that "a full-screen bitmap must be palette-reduced to fit the 128 KB watch-face
limit" did not survive measurement either: the simulator reports ~10 kB of app memory used with
the background loaded, because on API 4+ devices bitmaps live in the separate graphics pool.
"""
import os

import numpy as np
from PIL import Image

import device_colour
import hr_gauge

# ---- the decorative machinery recedes behind the data
# User request: "the intricate gears and pipes in the background are visually interesting but
# compete with the actual data; slightly dimming or blurring the background texture will help the
# time, date and metrics stand out". Applied to the FITTED frame and BEFORE the AMOLED correction,
# so the dimmed brass goes through the same warm-hue correction as everything else.
# The box is the gear cluster between the two dials, under the counter; the drum digits (screen
# y 229..267), the counter's own bottom plate (y 268..277), the dial faces, the ring letters and the
# tubes are all outside it and untouched. Measured on the shipping frame, the machinery in this box
# goes from mean luminance 31.6 to 19.9 (x0.63) with the counter's plate unchanged.
# User picked the no-blur variant: dim only, so the brass keeps its edges and texture.
GEAR_REGRESS = (86, 278, 234, 360)    # screen box (x0, y0, x1, y1)
GEAR_DIM = 0.35                       # fraction of the region's brightness removed at its centre
GEAR_FEATHER = 14                     # px the dim takes to fade out left, right and below
GEAR_FEATHER_TOP = 2                  #...and above: the box's top sits in the dark seam under the
                                      # counter, so a near-hard edge cannot show as a band
# The two lamps in that pocket are LIGHT SOURCES, not machinery: dimming a lit bulb is wrong, so
# each gets a hard exclusion (centre x, y, radius) with a small feather. Measured on the fitted
# frame: the amber lamp's bulb is box (107,286,15,14) and the green one's is (197,288,13,12).
LAMPS = ((114, 293, 15), (203, 294, 16))
LAMP_FEATHER = 3


def recede(img):
    """Return `img` with the machinery behind the counter dimmed by GEAR_DIM, feathered at the edges.

    The lit lamps inside the box are excluded: they are the pockets' light sources, and a bulb that
    dims with the gears behind it reads as a dead lamp.
    """
    x0, y0, x1, y1 = GEAR_REGRESS
    yy, xx = np.mgrid[0:img.height, 0:img.width].astype(np.float32)
    dx = np.maximum(np.maximum(x0 - xx, xx - x1), 0.0)
    dy_above = np.maximum(y0 - yy, 0.0)
    dy_below = np.maximum(yy - y1, 0.0)
    m = (np.clip(1.0 - dx / GEAR_FEATHER, 0.0, 1.0)
         * np.clip(1.0 - dy_above / GEAR_FEATHER_TOP, 0.0, 1.0)
         * np.clip(1.0 - dy_below / GEAR_FEATHER, 0.0, 1.0))
    for lx, ly, lr in LAMPS:
        d = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2)
        m = m * np.clip((d - lr) / LAMP_FEATHER, 0.0, 1.0)
    m = (m * GEAR_DIM)[..., None]
    return Image.fromarray(np.clip(np.asarray(img, np.float32) * (1.0 - m), 0, 255)
                           .astype(np.uint8), "RGB")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "artwork", "cand_split.png")   # written by prepare_artwork.py
DRW = os.path.join(HERE, "resources", "drawables")
os.makedirs(DRW, exist_ok=True)

if __name__ == "__main__":
    src = recede(Image.open(SRC).convert("RGB"))
    print("source", src.size)

    corrected = device_colour.correct(src)
    # the HR zone gauge's dim band, baked AFTER the correction (its colours are corrected
    # by hr_gauge itself, so they are never corrected twice)
    corrected = hr_gauge.bake(corrected)
    corrected.save(os.path.join(DRW, "background.png"), optimize=True)
    print(f"  background.png         full colour, AMOLED-corrected "
          f"(warm hue +{device_colour.HUE_SHIFT_DEG:g} deg, sat x{device_colour.SAT_SCALE:g})")

    # launcher icon: 40x40, the tubes + manifold (the most identifiable part). The split layout
    # puts the tubes across the full width of the top, so a full-width square from the top edge.
    icon = corrected.crop((0, 0, 320, 320)).resize((40, 40), Image.LANCZOS)
    icon.save(os.path.join(DRW, "launcher_icon.png"))
    print("  launcher_icon.png      40x40")
