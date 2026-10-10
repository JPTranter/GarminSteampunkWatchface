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

from PIL import Image

import device_colour
import hr_gauge

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "artwork", "cand_split.png")   # written by prepare_artwork.py
DRW = os.path.join(HERE, "resources", "drawables")
os.makedirs(DRW, exist_ok=True)

if __name__ == "__main__":
    src = Image.open(SRC).convert("RGB")
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
