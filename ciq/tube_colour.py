"""Generate source/TubeInk.mc: the tube digits' and separator's ink colours.

WHY a generated file: the digits are drawn LIVE by the view (drawText with a halo ring), unlike the
background artwork, which is baked and then pre-corrected once by device_colour.correct(). A colour
drawn live has to go through the SAME correction or the digits disagree with the glass they sit in
on the AMOLED panel - and warm colours are exactly where the panel shifts (device_colour.py). Writing
the corrected values into a generated .mc both enforces that and keeps one source of truth.

The three colours build one digit, painted back to front:
    INK_GLOW2  outer halo ring (radius 3)
    INK_GLOW1  inner halo ring (radius 1)
    INK_TIME   the glyph core, which carries the contrast and never pulses
The TARGET values below are what the face should look like ON THE WATCH (measured off the user's
reference photograph: a warm white-peach core inside an orange discharge, with the two rings
swapped relative to the earlier build so a dark channel separates the wire from its bloom).
run `python make.py assets` after editing.
"""
import os

from PIL import Image

import device_colour

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_MC = os.path.join(HERE, "source", "TubeInk.mc")

# Target colours AS SEEN ON THE WATCH (sRGB, before the AMOLED pre-correction).
INK_TARGET = {
    # The wire is ONE glyph pass: INK_TIME is the wire itself, and INK_GLOW1 (the 1 px band painted
    # under it) is its orange rim, so the stroke reads white-hot with a warm edge — the user's "the
    # center part of the clock digit should be more towards white". A two-pass version was built
    # first (orange glyph + a 1 px-eroded white glyph over it) and measured: at a 5 px stroke the
    # eroded core is ~1 px and barely visible, so the whole stroke is white and the rim comes from the
    # band. Measured off the user's second reference (a warm amber tube band): core (245,155,30) at
    # hue 35 deg / L 0.63, stroke body (182,102,22) at hue 30 / L 0.44, the glow into the glass at
    # (117,61,11).
    #
    # The core first shipped one step HOTTER than that (252,196,96) to buy contrast - 7.5:1 against
    # the amber glass where the exact reference match measures 6.2:1 - and the user, looking at the
    # watch, overruled the trade: "The time display is not orange enough. It should be like the
    # reference." A device observation is the only measurement taken from the panel, so the wire body
    # is now the reference's own (245,155,30), still 6.2:1 on the glyph core with a 5 px stroke.
    # A user-supplied ZOOM of the target wire fixed the ladder exactly, centre to outer:
    # (f8f7d4, f5e67d, f5e67d, f5e67d) - a cream core inside a yellow wire - with orange rings outside
    # it, measured off the same zoom (229,147,54) at 1-2 px out and (188,82,34) at 3-4 px. So the wire
    # is TWO passes (INK_WIRE paints the whole glyph, the eroded NixieTimeHot paints the core over it)
    # and the three bands are the orange falloff. These are as-seen values: the AMOLED pre-correction
    # is applied on the way out, exactly as for the baked artwork.
    "INK_TIME": (0xF8, 0xF7, 0xD4),  # the wire's cream core (eroded glyph, drawn last)
    "INK_WIRE": (0xF5, 0xE6, 0x7D),  # the wire's yellow body (the whole glyph)
    # The glow is STATIC at the bright baseline (user decision): the ring no longer pulses, so it is
    # stored at the colour the pulse used to reach at its peak. No headroom is needed now that
    # nothing scales it. A 1 px halo around the glyph is most of what the digit's colour IS at this
    # size, so the ring, not the core, is what the digit reads as - it carries the reference's stroke
    # body colour, one step below the core.
    # The bloom is THREE stepped bands, because drawText has no alpha and a bitmap font cannot be
    # blurred: a soft falloff can only be hand-painted as solid offsets of the glyph. Measured against
    # the reference's own profile (ciq/ref_glow.py, converted to our px: L32 at 1.2 px out, L21 at 2.3,
    # L15 at 4.0, L11 at 6.8, L3 at 11.4), this ladder plus the tightened glass haze lands at
    # L26 / L16 / L12 / L11 - so the digits read as a glowing wire instead of a bright glyph on a
    # washed-out tube. GLOW_RAD2 == GLOW_RAD1 would skip the middle band, and a radius equal to the
    # next one inward is skipped in the same way.
    "INK_GLOW1": (229, 147, 54),    # the orange ring just outside the yellow (measured)
    "INK_GLOW2": (188, 82, 34),     # next ring out (measured)
    "INK_GLOW3": (150, 62, 26),     # the fade step into the dark glass
}


RED_SHIFT = 0.0    # walk the whole ink ladder toward red; 0 ships the user's hex spec exactly


def toward_red(colour, k=RED_SHIFT):
    """The user, on the watch, twice: first "not orange enough", then "it still looks yellow - add 10%
    more red". A direction from the wrist is the decision, so this is applied to EVERY ink layer (core
    and all three bloom bands) rather than to the core alone - the digit reads as its bands as much as
    its core, and shifting only one of them moves the hue of the digit's edge away from its middle.
    Red goes up toward 255 and green/blue come down, so the hue walks toward red instead of merely
    brightening. Measured as-seen: core (242,145,32) at 0.00 -> (246,140,27) at 0.10 -> (247,124,24)
    at 0.20, i.e. hue 32 -> 31 -> 30 deg against the reference's 35. It is 0.00 now: the user then
    supplied the target ladder as exact hex values for a cream-and-yellow wire, which a red walk would
    immediately falsify.
    """
    r, g, b = colour
    return (round(r + k * (255 - r)), round(g * (1 - k)), round(b * (1 - k)))


def corrected(colour):
    row = Image.new("RGB", (1, 1), tuple(colour))
    return device_colour.correct(row).getpixel((0, 0))


def main():
    out = {}
    for k, v in INK_TARGET.items():
        out[k] = corrected(toward_red(v))
    with open(GEN_MC, "w", newline="\n") as f:
        f.write(f"""// GENERATED by ciq/tube_colour.py - do not edit; re-run `python make.py assets`.
// The tube digits' ink, already run through the AMOLED pre-correction (device_colour.py), so what
// the panel shows is the target colour in tube_colour.py. Painted outer ring -> inner ring -> core.
import Toybox.Lang;

const INK_WIRE = 0x{out['INK_WIRE'][0]:02X}{out['INK_WIRE'][1]:02X}{out['INK_WIRE'][2]:02X};
const INK_TIME = 0x{out['INK_TIME'][0]:02X}{out['INK_TIME'][1]:02X}{out['INK_TIME'][2]:02X};
const INK_GLOW1 = 0x{out['INK_GLOW1'][0]:02X}{out['INK_GLOW1'][1]:02X}{out['INK_GLOW1'][2]:02X};
const INK_GLOW2 = 0x{out['INK_GLOW2'][0]:02X}{out['INK_GLOW2'][1]:02X}{out['INK_GLOW2'][2]:02X};
const INK_GLOW3 = 0x{out['INK_GLOW3'][0]:02X}{out['INK_GLOW3'][1]:02X}{out['INK_GLOW3'][2]:02X};
""")
    print(f"wrote {os.path.relpath(GEN_MC, HERE)}  " + " ".join(
        f"{k}={v}" for k, v in out.items()))


if __name__ == "__main__":
    main()
