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

The numbers came from ONE phone photo of an older build — treat them as a first estimate and
confirm on the watch (make_calibration.py builds a side-by-side strip for exactly that).
"""
import numpy as np
from PIL import Image

HUE_SHIFT_DEG = 11.0   # measured: watch 17 deg vs monitor 28 deg for the same brass
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
