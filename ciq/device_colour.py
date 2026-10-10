"""Pre-correct artwork for the Venu Sq 2's AMOLED panel, which renders warm tones redder than sRGB.

WHY: photographed side by side with the simulator on a monitor (same photo, so the camera's own
bias largely cancels), the watch showed the brass at hue ~17 deg against the monitor's ~28 deg,
G/R 0.54 vs 0.69, and slightly MORE saturated (0.65 vs 0.58). The simulator capture matches the
source bitmap exactly (hue 31 deg), so the compiled bitmap is right and the shift happens on the
panel. The brass reads as copper/orange on the wrist.

The correction pre-rotates WARM hues toward yellow and trims their saturation, so the panel's shift
lands back on the intended brass. It is weighted to warm hues only (full effect 0-50 deg, fading
to zero by 80 deg and below 340 deg) so the blue sparks, the blue lamps and the green/orange
indicator lamps keep their colour. Blacks are untouched (hue rotation does nothing at V=0, and the
weight also fades out in the darkest pixels so near-black noise does not pick up a green cast).

RE-CALIBRATED ON THE PANEL (the original 11.0 deg came from one photo and over-rotated): a later
photo of the watch beside the monitor measured the mid brass matching to 0.0 deg but the brightest
and darkest warm tones 3-4 deg yellower than the design, so the shift was re-picked by eye off
`make_calibration.py`'s repeated-band screen, which shows the same hardware pre-corrected at +4, +8,
+11 and +14 deg. The user picked the TOP band: HUE_SHIFT_DEG = 4.0. Note it is the end of that
ladder, so the true value could be lower still - if the brass reads too red/copper on the wrist,
calibrate again with a ladder below it (0 / 2 / 4 / 6).

The SAT_SCALE value is still the original estimate (0.90 from 0.65 vs 0.58); the same photo
suggested it is also slightly over-trimmed (the panel measured +0.13 saturation on warm pixels).
It is a separate axis and can be calibrated the same way.

Judge a calibration screen ON THE WATCH, against real brass - not against the monitor's own copy of
it: each band carries its own pre-rotation, so only the band matching the assumed shift shows the
design colours there.
"""
import numpy as np
from PIL import Image

HUE_SHIFT_DEG = 4.0    # re-calibrated on the panel (see below), not the 11.0 of the original photo
SAT_SCALE = 0.90       # measured: watch 0.65 vs monitor 0.58 saturation


def warm_weight(h_deg, v):
    """1.0 for brass/copper hues, fading to 0 outside them and in near-black pixels."""
    hw = np.clip((80.0 - h_deg) / 30.0, 0, 1) * (h_deg <= 80)    # 0..50 full, 50..80 fade
    hw = np.where(h_deg >= 340, np.clip((h_deg - 340) / 20.0, 0, 1), hw)
    vw = np.clip((v - 0.04) / 0.08, 0, 1)                       # fade out below V ~0.12
    return hw * vw


def correct(img, hue_shift_deg=HUE_SHIFT_DEG, sat_scale=SAT_SCALE):
    """Return a copy of `img` (RGB) with warm hues rotated by +hue_shift_deg and desaturated."""
    hsv = np.asarray(img.convert("RGB").convert("HSV"), dtype=np.float64)
    h = hsv[..., 0] * 360.0 / 255.0
    s = hsv[..., 1] / 255.0
    v = hsv[..., 2] / 255.0
    w = warm_weight(h, v)
    h2 = (h + hue_shift_deg * w) % 360.0
    s2 = s * (1.0 - (1.0 - sat_scale) * w)
    out = np.stack([h2 * 255.0 / 360.0, s2 * 255.0, v * 255.0], axis=-1)
    return Image.fromarray(np.round(out).clip(0, 255).astype(np.uint8), "HSV").convert("RGB")


def as_seen(img):
    """Approximately undo correct(): what the corrected frame looks like ON the watch's panel,
    for README / store screenshots viewed on an sRGB monitor (where the pre-corrected frame
    itself looks yellow-green). An approximation - the panel is the truth - but it is the
    inverse of the same measured shift."""
    return correct(img, hue_shift_deg=-HUE_SHIFT_DEG, sat_scale=1.0 / SAT_SCALE)
