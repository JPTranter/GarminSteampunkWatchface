"""Mockup: the red rung on the tube ink. Decision support.

The user, on the watch: "it still looks yellow - add 10% more red". Shipped at k = 0.10
(tube_colour.RED_SHIFT, applied to every ink layer); this renders the rung above it so the next
request, if it comes, is a letter rather than another round of guessing.

Writes artwork/red_ladder.png.
"""
import os

import numpy as np
from PIL import Image

import amber_candidates as ac
import device_colour
import preview
import tube_colour

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "red_ladder.png")
BG = os.path.join(HERE, "resources", "drawables", "background.png")


def frame(k):
    c = dict(preview.parse_constants())
    for name, target in tube_colour.INK_TARGET.items():
        c[name] = int.from_bytes(bytes(tube_colour.corrected(tube_colour.toward_red(target, k))), "big")
    face = preview.render(consts=c, hr=128, background=Image.open(BG).convert("RGB"))
    return device_colour.as_seen(face)


def ink_seen(face):
    """Median colour of the lit ink inside the tubes (bright, saturated, warm)."""
    a = np.asarray(face, np.float32)
    c = preview.parse_constants()
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    box = np.zeros(a.shape[:2], bool)
    for cx in c["TIME_X"]:
        box[max(0, c["TIME_Y"] - 48):c["TIME_Y"] + 48, cx - 26:cx + 26] = True
    sel = (mx / 255.0 > 0.75) & (sat > 0.5) & box
    return np.median(a[sel], axis=0)


if __name__ == "__main__":
    rows = []
    print(f"{'red shift':>10s}  {'ink as seen':22s}  hue   note")
    for k, note in ((0.0, "before (the yellow one)"), (0.10, "SHIPPED"), (0.20, "next rung"),
                    (0.30, "deep red")):
        face = frame(k)
        med = ink_seen(face)
        r, g, b = med
        hue = 60 * (((g - b) / max(1.0, r - min(g, b))) % 6) if r >= g >= b else float("nan")
        print(f"{k:10.2f}  ({r:4.0f},{g:4.0f},{b:3.0f})        {hue:4.0f}  {note}")
        rows.append((f"k={k:.2f}  ink ({r:.0f},{g:.0f},{b:.0f})  hue {hue:.0f}  {note}", face))
    ac.sheet(rows, OUT, True)
    print("\nreference ink: (245,155,30), hue 35 deg")