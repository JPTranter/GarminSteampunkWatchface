# Steampunk Watch Face — Garmin Venu Sq 2 — Build Spec

## Deliverable
PNG watch-face mockups, **exactly 320 x 360 px**, one per iteration, portrait.

## Target device
Garmin Venu Sq 2 — 1.41" AMOLED, 320 x 360 px, round-rect body. Treat the whole
320x360 panel as the canvas (Garmin crops corners on the device; keep critical
content inside a ~292 x 332 safe area, i.e. >=14 px margin from each edge).

## Required on-screen data (all four must be clearly readable)
| Element | Mock value | Notes |
|---|---|---|
| Time   | 10:09 | classic watch-advertising position; analog hands must show ~10:09 |
| Date   | WED 30 SEP | weekday + day number required; month optional but nice |
| Heart rate | 72 bpm | number required, unit small; a subtle heart glyph helps identify it |
| Steps  | 8,342 | number required; a footprint/chevron glyph helps identify it |

These values are the mock data for every iteration — do NOT invent other values,
so iterations stay comparable.

## Readability rules (the reviewer scores these)
1. **Contrast**: text/digits must sit on a surface with >= ~4.5:1 luminance ratio.
   Never put dark numerals on mid-tone brass without a plate or an outline.
2. **Size floor**: time >= 30 px tall for analog-equivalent, digits >= 16 px cap height
   for HR/steps/date. Nothing that carries data may be smaller than 12 px cap height.
3. **Never overlap**: hands must not cross the date window, HR or steps numbers.
   Decorative gears/ornaments must not sit under or behind any digit.
4. **Hierarchy**: time first, then date, then HR and steps. A viewer reads the time
   in under one second without hunting.
5. **Ambiguity**: do not use a font whose 0/O, 1/I, or 6/8 are confusable at these sizes.
6. **Number legibility on dark plates**: amber/ivory digits on near-black plate = best.

## Steampunk styling rules (the reviewer scores these)
- Palette: brass, copper, bronze, gunmetal/iron, ivory enamel, oxblood red, verdigris.
- Materials: brushed metal, concentric turning marks, patina, enamel dials, rivets,
  slotted screws, copper pipes, exposed gears/cogs, leather straps.
- Typography: engraved serif (Garamond, Baskerville, Bookman, Centaur, Times, Georgia);
  Old English / Script MT Bold only for ornament or banners, never for data digits.
- Finish: chiselled/embossed text, bevels, vignette, subtle glass glaze.
- Avoid: flat clip-art gears with no shading, neon/cyber colours, sans-serif tech look,
  emoji, hard aliased edges.

## Rendering environment
- Python: **use the explicit path `/c/Python314/python.exe`** (Python 3.14.0, Pillow 12.3.0,
  numpy 2.5.2). The bare `python` on PATH is currently a broken shim that exits 127 with no
  output — run scripts as `/c/Python314/python.exe myscript.py`, and add `-u` when
  debugging so output is not lost if a run aborts.
- Working dir: `<repo root>`
- Shared library: `steampunk_lib.py` (import it; do not edit it).
  Provides canvas/SUPERSAMPLE, PALETTES, fonts, gradients, gears, rivets, screws,
  pipes, engraved/emboss/glow text, tick rings, arc gauges, plates, vignette, glaze,
  patina, noise. Read its docstrings before writing drawing code.
- Render at SUPERSAMPLE x3 and call `finish()` to get the 320x360 PNG.

### v2 primitives (use these for the enhanced brief)
- `fit_cap(text, font, cap)` — font whose rendered **digit ink height** is exactly `cap`
  final px. The only reliable way to hit a size floor; do not hand-tune point sizes.
- `ink_height(text, font)` — real ink height of the glyphs in a string. **Fitting is done
  against this, not the nominal cap**, because most installed serif faces use *old-style
  figures* (3,4,5,7,9 descend; 6,8 ascend) so a number's ink box is taller than its cap.
- `lining_figures(font) -> bool` — only **`times_bd`** among the serif set has lining
  figures; `garamond_bd`, `bookman_bd`, `georgia_bd`, `centaur`, `constantia_bd` and
  `baskerville` are all old-style. Use `times_bd` for drum/digital windows where uniform
  digit heights matter, and keep the old-style faces for ornamental analog numerals.
- `drum_window(img, xy0, xy1, text, cap=44, ...)` — recessed black drum with guaranteed
  digit size, roller shading, an optional `ghost` of the adjacent drum digit, and a glass
  glint. Returns the digit ink bbox; use it to check the >=8 px clearance rule.
- `plate3d`, `recess`, `crystal` — extruded plate, countersunk window, glass sheen (depth).
- `gear_layer(cx, cy, r, ...)` — a shadezd cog with directional lighting and a lit rim
  (use this, not the flat `draw_gear`, when the cog is visible).
- `belt_run(img, p0, p1, width, ...)` — segmented belt with plates, rivets, a ruled tick
  scale, end rollers and motion cues.
- `riveted_rail` / `knurled_crown` / `spark` (additive flare) — hardware and light.
- `verify_clearance(data_bbox, obstructions, min_gap=8.0)` — the brief's data-clearance check.


## Iteration naming
`iterations/iter_<NNN>_<slug>.png` (NNN = 3-digit global iteration number, 001..100).
Every rendered face must be a complete, self-contained PNG at 320x360.

## Loop protocol
1. **Generator agent** produces a batch of distinct variants (different layout,
   palette, font, gear arrangement, hand style) and renders each to PNG. It must
   act on the reviewer's previous feedback, not merely re-roll randomness.
2. **Reviewer agent** inspects every PNG, scores each of the 4 data elements for
   readability plus steampunk alignment, and returns per-image scores, the single
   best image, concrete defects, and a verdict: `APPROVED` or `REVISE`.
   The reviewer's authoritative rubric is `reviews/rubric.md` — read it, it defines the
   scoring anchors, the mandatory-defect list and the anti-goalpost rules.
3. Loop ends when the reviewer returns APPROVED or the global iteration counter hits 100.

## Frozen approval bar (target for the generator)
An iteration is accepted as soon as the reviewer scores it **zero mandatory defects** and
**time >= 9, date >= 7, heart rate >= 7, steps >= 7, steampunk >= 7**, with the four mock
values exactly correct. The reviewer may not add criteria mid-loop (see rubric §5), so
this bar is the exact target: aim at it and stop when it is reached. Style polish beyond
the bar is explicitly optional and must not be pursued at the cost of the loop's budget.

## Style north star (set by the user)
A steampunk wristwatch the user pointed at as the reference (a third-party product photo, kept
outside this repo): rectangular case, riveted brass rails top and bottom, open-work mechanism
behind a glass crystal, huge white/ivory digits on black rotating drums with engraved
letterspaced brass labels (HOUR / MINUTE / SECONDS) on riveted plates, fine ruled tick scales
along the belt tracks, deep inter-layer shadows, brass reading as real metal.

**Study the described direction before designing.** The open-work drum-window family is the priority
direction; an enamel analog dial is acceptable but scores lower on steampunk alignment.
The most readable presentation of the time is a large white-on-black drum window — the
rubric scores that channel generously (see rubric §1.1b), so use it when the composition
allows. Readability still outranks style fidelity.

## Aesthetic brief (user, verbatim intent — governs every round from round 2 onward)

> "A retro-futuristic aesthetic that blends 19th-century Victorian or Edwardian fashion
> with industrial, steam-powered, and mechanical technology." — i.e. steampunk. Extra
> "wow" for a copper/brass appearance with **belts and cogs and highlights of sparks**,
> but it cannot ruin readability. **3D depth** usage is also important.

### 0. Welcome concept families (user-flagged, plus researched ones)
The user has explicitly called out **nixie tubes** as a good-looking option, so nixie
concepts are first-class in this project: a glass envelope with a warm amber/violet
discharge glow, stacked wire numerals seen through the glass, a brass collar/socket with
the pin ring, a soft halo bleeding into the surrounding metal, and the dim silhouette of
the inactive numerals behind the lit one. That silhouette trick is exactly the "drum
ghost" idea in `drum_window` — reuse the logic, change the material story.

Other display technologies worth a concept each: split-flap drums, mechanical clock
drums, edge-lit engraved glass, watchmaker's balance/escapement, Wimshurst or Tesla
coil, telegraph/teleprinter tape, barometer/altimeter dial stacks, orrery and planetary
gearing, difference-engine columns, Edison bulb filaments, and railway station
departure boards.

### 1. Required "wow" vocabulary (each face should carry at least three)
- **Belts**: visible belt/track runs — a loop of segmented plates with rivets and a fine
  ruled tick scale, wrapping at least one drum or running past the data windows. Belts
  should show *motion* cues: a direction, a slight offset between plates, a highlighted
  leading edge where a plate turns over the roller.
- **Cogs**: a real gear train, not one token cog — at least three cogs at two or more
  scales, with visible tooth engagement (teeth of adjacent cogs overlapping in phase),
  spokes, hubs and bores. Some may be partly occluded by plates in front of them.
- **Sparks**: small additive light flares (2–6 px core with amber→white falloff) with a
  short directional streak, as if struck where metal meets metal. 2–5 per face.
- **Copper/brass material realism**: anisotropic brushed sheen that follows the surface's
  turning direction, colour variation between polished and oxidised areas, specular
  highlights on raised edges, darkened crevices. Brass and copper must look like *metal*,
  not brown paint.

### 2. 3D depth is a first-class requirement, not a nicety
Show at least four of: layered depth (foreground rails crisp / mid plates / background
mechanism), true drop shadows between layers with ambient occlusion where parts meet,
bevelled edges lit consistently from one direction (upper-left by default) with
highlight + core + shadow bands, a glass crystal with a highlight streak and a faint
reflection of the mechanism, perspective on the belt tracks (converging scale), and
depth-of-field softening on the farthest layer. A flat face with painted-on shading
scores low regardless of its palette.

### 3. The readability veto (this outranks every wow element)
Sparks, cogs, belts and highlights are **hard-vetoed anywhere they touch data**: no spark,
tooth, rivet, belt plate, highlight streak or shadow may overlap a data glyph, and each
must stay ≥ 8 px clear of any digit's bounding box. Decorative elements may cross plates,
rails and empty background freely. A face that gains a spark but loses a legible "8,342"
is a regression, and the reviewer will say so.

## WORKING TWO-PHASE LOOP (how the 100 iterations are spent)

The goal is **not** a perfect face from the outset. It is to **iterate fast, throw out a
lot of ideas, find the cool ones, and only then form those into a usable clock face**.
Perfectionism applied to a rough concept wastes the budget; so the loop runs in two modes.

### Phase A — CONCEPT SWEEP (fast, high variance, breadth over polish)
Produces the raw ideas. Rules:
- Each iteration is a **concept**, not a finished face: distinct in its fundamental
  organising idea (what the display IS and how it is built), not a repaint.
- **Speed over polish.** Rough edges are expected and must not be "fixed" — a concept
  exists to answer the question "is this idea cool?".
- Data may be schematic (tiny or approximate) but the concept must show where the four
  data elements will live.
- Use **web search** to find fresh inspiration (real Victorian engineering, nixie tubes,
  difference engines, orreries, astronomical regulators, barometers, telegram hardware,
  Edison bulbs, hairspring regulators, steam gauges, cylinder/rotary escapements,
  Gyro-compass repeaters, railroad pocket watches). Research, then design — do not
  re-derive the same handful of ideas from memory.
- The reviewer **ranks and triages** in this phase; it does NOT gate on readability.

### Phase B — FORM INTO A USABLE FACE (readability gates now apply)
Takes the concepts the reviewer picked and forms each into a real Venu Sq 2 face: exact
digit sizes, contrast, clearance, safe area. This is where the frozen bar in the rubric
applies and where a face can be APPROVED.

**A face is only ever APPROVED in Phase B.** A Phase A concept cannot be approved, because
it was never trying to be a finished face — it only has to earn a promotion.

### Phase A concept scorecard (reviewer, out of 10 each)
1. **Idea strength** — is the organising idea genuinely new for this project and interesting?
2. **Cool factor** — would a person show this to a friend?
3. **Steampunk fidelity** — Victorian/Edwardian + industrial/steam/mechanical, with copper/
   brass, belts, cogs, sparks and 3D depth.
4. **Feasibility** — can it actually be formed into a usable face at 320x360 without
   losing the idea or the readability of all four data elements?

Verdicts in Phase A: **PROMOTE** (form into a usable face), **PARK** (keep the idea,
not now), or **KILL** — plus one line on what to change. The reviewer may return
`REJECT_ALL` to declare a whole family dead and demand fresh directions.

## Iteration budget and reject-all authority
- The global counter runs to **100** iterations. Batches are 10, so rounds 1..10. Round 1
  (iterations 001-010) was rendered before this brief was published; the enhanced criteria
  are recorded as NOTEs against it and gate verdicts from **round 2 onward** (rubric §5
  rule 2).
- 10 iterations are spent (001-010). **90 remain.**
- The reviewer may return **`REJECT_ALL`**: reject the entire batch, declare the current
  concept family a dead end, and instruct the generator to abandon it and propose a
  completely fresh concept (a new concept must differ in its fundamental organising idea —
  layout logic, data presentation and material story — not merely its palette or
  ornamentation). On REJECT_ALL the generator must NOT iterate on the rejected family.


