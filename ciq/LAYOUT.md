# Venu Sq 2 layout — artwork fit and text coordinates

## Why the artwork had to be re-fitted
The supplied artwork is **1024×1024 square** with the device spanning **951×766** inside it — wider
than tall. The Venu Sq 2 screen is **320×360 PORTRAIT** (aspect 0.889). A landscape device cannot
fill a portrait screen, so something has to give. Three options were generated and compared
(`ciq/artwork/_compare.png`):

| Option | Result |
|---|---|
| **A — fit** (scale 0.3125) | whole device visible but letterboxed top and bottom, ~80 px of screen wasted |
| **B — fill** (scale 0.4371) | fills the screen but **crops into both round gauges** — data areas, so unusable |
| **C — width** (scale 0.3365) | shipped first. Device spans the full 320 px width, centred vertically; the art's own black surround forms the top/bottom bands, so they read as bezel rather than dead space |

### Current: the split-scale layout (supersedes the width fit)
The width-fit left the tubes ~210 px wide and every readout small. The user asked for the tubes to
fill the top and the dials to fill the bottom, with the dials' outer edges allowed off-screen.
**One uniform scale cannot do that**: the dial centres sit at x 207 / 813 on the 1024 grid, so above
~0.38 a dial's readout leaves the screen before the tubes fill the width. Three mockups were shown
(`artwork/zoom/_zoom_compare.png`, made by `zoom_candidates.py`) and the user chose **C**:

| Band | Source rows | Scale | vs old |
|---|---|---|---|
| top — tubes + manifold | y < 506 | 0.49 | ×1.456 |
| bottom — dials, counter, gears | y ≥ 506 | 0.43 | ×1.278 |

The halves join at source y 506 (the dark gap under the manifold; screen y ≈ 219) with an 8 px
feather — no visible seam. The outer sparks and side pipes are cropped; the tube tips touch the top
edge. `prepare_artwork.py` also inpaints the
heart-rate dial's winged pointer out of the dial face (user request).

```
top:    screen = ((src_x - 512) * 0.49 + 160,  src_y * 0.49 - 29.4)
bottom: screen = ((src_x - 512) * 0.43 + 160, (src_y - 506) * 0.43 + 218.5)
```

### Zoomed out 5 %, and every position generated (current)
At the user's request the split scales went to **0.4655 / 0.4085** (C × 0.95), with the tube tips
6 px below the top edge, so the tubes have room and more of both dials shows. Rather than
re-measure, every on-screen position is now *generated* from the scales by
`prepare_artwork.py` into `source/Layout.mc`: tube digits, the five step drums and their
windows, the HR and day numbers, the arc channels. The HR gauge (`hr_gauge.py`), the date ring
(`make_date_ring.py`) and the font sizes (`make_fonts.py`) take their geometry from the same
`geometry()`. Points measured on a screen are converted once to the 1024 grid and mapped
forward. Check: feeding layout C back through `geometry()` reproduces every hand-measured value
that shipped on it, exactly. A zoom change is now the one `ST, SB, TOP_Y` line.

The tube envelopes are re-lit as clear blue glass before the split (`glass_tubes`; see
LESSONS L56), and the step counter now uses all **five** drum windows the art has (dividers at
screen x 99 / 122 / 144 / 167 / 190 / 214, window y 229..267 on this frame).

### The original uniform transform (history)

Scale `0.3365`, crop origin `(12, -31)`. Source → screen transform:

```
screen_x = round(src_x * 0.3365 - 12)
screen_y = round(src_y * 0.3365 + 31)
```

## Shipping background
`ciq/artwork/cand_split.png` (full colour, from `prepare_artwork.py`) → `prepare_resources.py`
(AMOLED colour pre-correction, `device_colour.py`) → `ciq/resources/drawables/background.png`
(full colour, compiled as **16-bit** with `automaticPalette="false"`) — 320×360, with the **"Made
with AI" watermark** filled pure black and the **heart-rate pointer** inpainted out. (The old
`resources/images/background.png` was a stale pre-fix copy and has been removed, as have the unused
16/64/256-colour variants.)

## Text coordinates on the 320×360 screen

The source points live in `prepare_artwork.py` (`POINTS`, on the 1024 grid) and the script prints
the screen table below. They are the values the watch face code must use — do not re-derive them by
eye on the small image. The source points are the earlier *shipped* coordinates mapped back through
the old transform, so the hand nudges made once real font metrics were known (HR lifted off BPM,
the date lines pushed off the dial rim) carry over to the new scale:

| Element | Shipped (x, y) | Old (0.3365) |
|---|---|---|
| Time tubes 1–4 | 47 / 125 / 193 / 275, y 96 | 83 / 136 / 183 / 239, y 117 |
| Steps drums 1–4 | 132 / 157 / 181 / 206, y 259 / 255 / 255 / 255 | 138 / 158 / 177 / 196, y 233 / 230 |
| Heart rate | 29, 274 (alone on the zone gauge; BPM removed) | 58, 229 |
| Weekday | ring patch at 245, 233 (one letter per segment) | 262, 221 |
| Day number | 288, 284 (NixieDay, 53 px ink) | 262, 253 |
| Month | ring patch at 246, 304 (one letter per segment) | 262, 282 |

The gauge rows were re-centred on the **measured** dials in the new frame (HoughCircles, plus a
luminance profile down each dial's centre column): the HR number is centred on the dial's dark
face (y 227..320) inside the zone gauge (`hr_gauge.py`: band r 34..42, opening left, 250 deg), the day number on the date dial's centre (288.1, 283.9).

**Date ring** (`make_date_ring.py`, user-approved): the weekday and month are set one letter per
segment of the date dial's outer ring, rotated to it, which frees the inner disc for a 53 px day
number. The 12 hand-drawn dividers were read off a polar unwrap of the dial (25, 58, 90, 122,
152.5, 179, 205, 241, 270, 299, 331, 357 deg; 0 = 3 o'clock, clockwise) and each letter sits on its
own segment's centre at r 44.7 px. Dividers fall on 12 and 6 o'clock and the right-hand segments
run off the screen, so both words lean left, mirrored: weekday 223 / 255.5 / 284.5 deg (tops out),
month 137 / 106 / 74 deg (tops in). The device cannot rotate text, so the 19 words are pre-rendered
as opaque 16-bit patches of the background with the letters blended in.

Note the two dials sit at **different heights** on the artwork (dial faces at y 605 vs 657 on the
1024 grid), which is why the heart rate and date readouts are not at the same screen y.

## Fonts (all custom — every built-in is too large)

Measured on the device, the smallest built-in font (`FONT_XTINY`) is 39 px and `FONT_NUMBER_MILD`
is 82 px. A bitmap font cannot be scaled at runtime, so **each size the layout needs is its own
font resource**, generated by `ciq/make_fonts.py`:

| Font | Atlas | Digit ink | Used for |
|---|---|---|---|
| `NixieTime` | 512×75 | 75 px | the four tube digits (was 53) |
| `NixieDay` | 512×53 | 53 px | the day number, alone in the date dial's inner disc (was NixieSmall, 32 → 42 px) |
| `NixieMid` | 512×37 | 37 px | the heart-rate number (was 29) |
| `NixieStep` | 512×29 | 29 px | the four odometer drums (was 23) |

Digit ink height is ≈ 0.67 × the point size passed to `make_fonts.py` (old-style serif figures;
see `docs/LESSONS_LEARNT.md` L11).

## Resource layout, class signatures and live-data calls — confirmed

The Connect IQ side is no longer open: `ciq/source/` builds and runs on the device, and the researched
answers (resource ids, `WatchFace` signatures, the live-data APIs with their null handling, the
measured built-in font heights and the 128 KB watch-face memory limit) are recorded with sources in
`plugindocs/CONNECTIQ_FACTS.md`. The coordinates above are independent of that and are final.

## Working on the face

```bash
python preview.py                      # offline 320x360 render, no build (reads the .mc constants)
python simshot.py                      # build, push to the running simulator, screenshot it
powershell -File push_watch.ps1        # sideload onto the watch over USB, then verify the copy
```

`preview.py` is the fast loop (a layout tweak in a second); `simshot.py` and `push_watch.ps1` prove it
on the simulator and on the watch, which stay the source of truth. See `docs/LESSONS_LEARNT.md` §8
for why all three exist and what each one cost to learn.
