# Steampunk Watch Face — Garmin Venu Sq 2 — Project Status

_Last updated: round 6 complete. Ledger: **60 / 100 iterations spent.** Stop condition met
(the reviewer returned all-approved verdicts in rounds 3, 4, 5 and 6). Remaining 40
iterations are unspent and available on request._

## Deliverable
Steampunk watch-face mockups, 320 x 360 PNG, one per iteration, for the Garmin Venu Sq 2
(1.41" AMOLED). Fixed mock data across all iterations so they stay comparable:
time **10:09**, date **WED 30 SEP**, heart rate **72 BPM**, steps **8,342**.

## How the loop runs
Two phases, defined in `SPEC.md`:
- **Phase A — concept sweep.** Fast, rough, breadth first. A concept only has to answer
  "is this idea cool?"; rough edges are expected and must NOT be polished.
- **Phase B — form into a usable face.** Finalists get built properly; the strict
  readability bar applies, and only here can a face be APPROVED.

Roles: a **generator** agent renders batches of 10; a separate **reviewer** agent scores
them against `reviews/rubric.md`. The reviewer may `REJECT_ALL` a whole family and demand
fresh directions. Loop ends on APPROVED against the enhanced bar, or at iteration 100.

## Ledger
| Round | Iterations | Phase | Outcome |
|---|---|---|---|
| 0 | 000 | reference | baseline enamel dial, REVISE (control) |
| 1 | 001-010 | B (pre-brief) | **7 of 10 cleared the original bar** (001,002,003,005,006,009,010). Best: `iter_003` 34/40 |
| 2 | 011-020 | A concept sweep | 10 distinct research-led concepts. PROMOTED: nixie rack, chart recorder, orrery. PARKED 6, KILLED 1 |
| 3 | 021-030 | B (form promoted) | **ALL 10 APPROVED** — bar met, claim independently verified. Best: `iter_025` / `iter_027` (40/40 readability, steampunk 8) |
| 4 | 031-040 | B (blueprint) | **ALL 10 APPROVED**. Blueprint matched: 4 tubes, manifold, heart gauge + odometer + weekday-ring date dial. Best: `iter_036` (40/40, time 15.9-16.1:1) |
| 5 | 041-050 | B (close 3 gaps) | **ALL 10 APPROVED**. Bolts 4 px median run (from 13-16), HR fill gauge 40 %, date hand on WE, 7/7 weekdays. Best: `iter_046` |
| 6 | 051-060 | B (arc realism) | **ALL 10 APPROVED**. Gutters 10→21-28 px, bolts verified blue-white spidery, chart halo proven removed. Best: `iter_060` |
| 7 | 061-070 | 3D component-first | Real-geometry components built and iterated; **assembled into one scene**. Final: `hybrid/FINAL_3D_face.png` |

## 3D phase outcome — components iterated, then assembled
Method the user set: **component-first, review after every iteration, learn each component's skills
before moving on, sparks last.** Every iteration is on disk as an image with a review entry.

| Component | What it reached | Attempts |
|---|---|---|
| nixie tube | Lathed envelope, tangent-continuous shoulder, drawn nipple with base bead, clear glass with refraction, internal speckle glow | 32 |
| tube socket | Four stepped collars, knurl bands, 14 pin rings each, valve bosses, dark manifold with recessed face, bolt row, 3 blue lamps | 19 |
| heart gauge | Brass bezel, black dial, graduated arc with ticks, blue segment, -40/180 labels, red heart needle on a boss | 13 |
| date gauge | Weekday ring, red hand, day-number position | 4 |
| step counter | Brass frame, five drums, divider bars, glass | 1 |
| **assembly** | All five in ONE scene at 320x360 — `hybrid/FINAL_3D_face.png` | 2 |

**Deliverables:** `hybrid/FINAL_3D_face.png` (320x360) and `FINAL_3D_face_2x.png`;
`hybrid/attempts/REVIEW.md` (per-iteration reviews and lessons); `hybrid/research/` (three sourced
technique guides); `hybrid/batch.py` (serial attempt runner + comparison sheets);
`docs/LESSONS_LEARNT.md` (project-wide, including the token/time-efficiency rules).

**Honest standing vs the reference:** structure and materials match well; *drama* does not yet. The
reference's tubes are larger relative to the frame and filled with a bright blue-white discharge, its
manifold has rounded machined fittings rather than flat plates, and the assembled digits measure
28-32 px against a 44 px bar.

**What the phase actually taught (the transferable part):** every major defect was **occlusion or
orientation**, never modelling skill — digits buried inside their own plate, a light's own surface in
frame, the rail's inset face inside the rail, the crystal squashed on the wrong axis, collar rims
facing the wrong way. Before editing a surface, establish what is actually in front of it; and when
two targeted fixes change nothing, stop tuning and instrument the scene to *name the object*.

## 3D / Blender phase (from iteration 061)
The user asked for the face rendered **in real 3D in Blender**, as close as possible to
`reference/nixie_moodboard_arcs.png`, with **no overlays except the digit glyphs** — every other
element (gauges, needles, weekday letters, labels, drums, rails, cogs) must be real geometry.

Two spikes established the approach and are worth reading before touching this:
- `spikes/001-blender-cycles-photoreal/README.md` — all-in-Cycles fails on the data: a
  self-luminous datum cannot hold the contrast bar (best 2.9:1 vs 12:1 required), because AgX
  compresses emissive glyphs while Standard clips them into their own bloom, and glass refraction
  smears a numeral behind it. Also documents the headless Blender traps (default startup Cube,
  relative render paths, axis-vs-depth, layer order, hollow tubes).
- `spikes/002-hybrid-machine-plus-data/README.md` — Cycles machine layer + controlled data layer
  works: time digits went from 2.9:1 to 12.5-13.8:1 at the 6 px ring. Weak point moved from the
  renderer to the data design.

**Method now in force (user's direction):**
1. **Component-first.** Build and validate each part on its own against its own reference crop
   before assembling: **nixie tube → tube base/socket → heart gauge → date gauge → step counter**
   (+ gear train). Crops live in `reference/crops/`, cut by `reference/cut_components.py`.
2. **Learn each component's skills before moving on.** Study the crop, research or prototype any
   unfamiliar modelling technique, build, render, compare, iterate — and only then start the next.
3. **Up to 50 attempts per component, every attempt stored as an image** in
   `hybrid/attempts/<component>/attempt_NNN.png` with a `LOG.md` line per attempt. The image
   trail is part of the deliverable; bad attempts are kept, not deleted.
4. **Sparks last.** No electric arcs in the component rounds — they render last, possibly via a
   Blender add-on, once the geometry underneath is right.

## Round 6 result — arcs fixed, loop stop condition met again
`reviews/round_06_review.md`: all ten APPROVED; best `iter_060_nixie-blueprint-match.png`.

- **Bolts are genuinely lightning now**, verified on saved pixels rather than the log: core
  band median (255,255,255) with B-R = 0, sheath (190,250,255) at B-R = +62, bloom
  (122,182,247) at B-R = +124 — white core, blue tendrils, blue bloom. Skeleton analysis
  gives 4-10 branch tips per side, 5-6 fork points per bolt, two fork levels, every discharge
  ≥31 px. Round 5's featureless 369/296 px tufts are gone.
- **Geometry fix confirmed:** measured clear channel 21/24/28/27/25/22/28 px per face against
  round 5's ~10 px. Clearance did not regress (worst 13.0 px, vs round 5's 10.0 px).
- **Halo removal proven by radial band profile:** round 5's iter_048 lifted 0.978 → 0.633
  across rings (a 2.6 pt spread); round 6's iter_057 is flat from 2 px out (0.49 pt spread).
  The paper is still aged stock, not a white band.
- **The darkness trade paid off:** chassis darkening cost no brass character (warm chroma kept,
  p95 highlight range actually rose 0.732 → 0.832) and bought 16 px-ring contrast — round 6
  nixie faces hold 11.5-13.5:1 where round 5's fell to 9.4-11.2:1.

**Honesty held up.** The generator pre-empted a claim failure this round rather than
overstating: it published the control measurement showing the ≥6 px bright run is mostly the
trunk, not the fork flares (round 5 had claimed the opposite). The reviewer reproduced it and
ruled the criterion optical, not numeric — the 13-16 px solid column is gone, which was the
actual requirement. It also caught two overstated details on its own side (a 1-2 px copper
filament does sit in the right channel; the sheath colours are paler than stated).

**Distance to the user's reference:** ~0.75-0.8 on arc character, closer on layout and
material. Two taste-distance gaps remain, both capped by the readability budget: the glass is
a deep envelope rather than true domed crystal, and our discharges are a dense bristle where
the blueprint has a few long clean spikes.

---

## FINAL DELIVERABLE
`iterations/FINAL_board_2x.png` — curated 2x board of the 8 best approved faces.
Curated picks, best first:

| Face | Why |
|---|---|
| `iter_060_nixie-blueprint-match.png` | **Best overall.** Blueprint match: 4 tubes, manifold, three-part band, deep glass, blue-white bolts, 28 px gutters |
| `iter_046_nixie-heavy-manifold-glass.png` | Richest hardware read (5 valve collars, bolt row, 3 indicator lamps) |
| `iter_053_nixie-max-gutter-spidery.png` | Widest channel, deepest tendril colour |
| `iter_036_nixie-heavy-manifold.png` | Round-4 best; the face that first matched the blueprint |
| `iter_057_chart-recorder-halo-free.png` | Chart recorder, honest paper contrast, cleanest large-format read |
| `iter_059_orrery-blue-white-bolts.png` | Orrery ring regulator with blue-white bolts |
| `iter_025_chart-recorder-no7.png` | Calmest read in the project (round-3 best) |
| `iter_021_nixie-rack-classic.png` | First approved nixie — the concept that led to the blueprint |

All 60 rendered faces are in `iterations/` (81 files including concept sketches, contact
sheets and verification logs). Every face is 320x360 PNG with the four mock values exact.

## Round 5 result — gaps closed; generator's numbers run warm
`reviews/round_05_review.md`: all ten APPROVED, all three round-4 gaps genuinely closed
(bolts 4.0 px median bright run vs round 4's 13-16 px columns; HR dial now a real fill gauge
with the red heart AS the needle; date dial with 7/7 weekdays and the hand on WE).

**Recurring pattern worth remembering:** the generator's self-reported precision is
consistently optimistic. It claimed needle and hand deltas of exactly 0.00°; the reviewer
measured 2.4° and 3.5°. It claimed 17.6:1 chart contrast; the reviewer measured 14.2:1. It
claimed the ≥6 px bright run was "confined to fork junctions"; the reviewer measured 23-37
such rows on the long side arcs. None changed a verdict, but no generator number in this
project should be treated as verified until the reviewer reproduces it — which is exactly
why the review loop re-measures rather than reads the generator's log.

**Per-stroke halo ruled cosmetic gaming (not a defect):** the chart faces' halo lifts exactly
the pixels the contrast test samples (14.2:1 at a 2 px ring vs 12.9:1 at 16 px) and reads as
an artificial outer glow. The face already clears the bar honestly at a 16 px ring, so the
halo buys nothing — removal was ordered for round 6.

**Remaining gap is geometric, not cosmetic:** the bolts read as white cracks because the
gutter either side of the tubes is only ~10 px, so 20-40° tendrils get clipped to stubs.
Round 6 pulls the tube row inward to widen the gutters to ≥20 px and re-cuts the bolts
blue-white and spidery (8-14 tendrils, two fork levels).

## Round 4 result — blueprint matched, three gaps measured
`reviews/round_04_review.md`: all ten APPROVED. Round 3's open items genuinely fixed —
every spark/arc/lamp now crests peak luminance **1.000** with a ≥6 px bright core (round 3
measured 0.21-0.24 on the nixie and 0.006 on the orrery) and every belt shows a real motion
cue. Contrasts re-measured at both 2 px and 6 px rings: worst data number 11.2:1. Blueprint
fidelity for the nixie family ~0.85, with the three deviations below.

**Clearance dispute settled on measurement:** the generator asked to be excused two sub-8px
readings. The reviewer ruled both **excused**, and not on the generator's reasoning — the
"4.9 px" figure was a padded-bounding-box artefact (true ink-to-ink distance ≥10 px), and the
"0.0 px screw" reading **did not reproduce at all**: the real distance is 52 px. Both claims
withdrawn on evidence. Worth remembering: a registered bounding box that carries bloom padding
is the wrong object to test clearance against.

**Three measured gaps carried into round 5:**
1. The arcs read as 13-16 px **solid columns**, not thin branching lightning. The mandatory
   ≥6 px bright core forces a chunky silhouette — the core must be split into a 3-4 px bolt
   plus ~1 px forked tendrils, keeping the ≥6 px run only at fork junctions.
2. The **heart-rate dial contradicts its number**: the arc spans the whole 0-180 scale and the
   heart sits mid-scale, so it is not a gauge. Needs a dark track, a fill to ~40% (72 of 180),
   and the heart as the needle resting at the fill's end.
3. The **date dial points at the wrong day**: the hand rests on MO/TU while the caption reads
   "TH WED", and only six weekday letters are printed. All seven needed, hand on WED.

Also standing: the tubes read flatter than the blueprint's domed glass — but the bloom and
glass interior cannot be lightened without dropping digit contrast from ~14:1 to ~3:1, so
this is a genuine budget tension, not just a skill gap.

## Round 3 result — the design loop's stop condition was met
`reviews/round_03_review.md`: all ten faces cleared the frozen bar (zero mandatory defects;
time ≥9; date/HR/steps/steampunk ≥7; correct mock values). The reviewer re-measured
everything itself: ink heights reproduced exactly (nixie 57 px, chart 52 px, orrery 49-51 px;
date 20-22 px; HR 20-23 px; steps 21-23 px), contrasts held at a *stricter* 6 px ring
(≥11.79:1 for every data number), data stayed inside the safe area, and the worst true
ornament gap was 8.0-8.3 px. No drift on the round-1 control.

**One claimed feature failed verification** — and it is the most important one for the
user's taste: the "2-5 additive sparks per face" claim did not hold. In the nixie faces the
sparks measured peak luminance 0.21-0.24 (invisible; killed by the vignette) and the
orrery's measured 0.006 (fully occluded behind a plate). Only the chart family carried
genuine sparks (core L=0.96). The reviewer also flagged weak belt motion cues.

That gap is exactly what the user's next reference demanded, so round 4 targets it.

## Round 1 result (reviews/round_01_review.md)
- Independently verified: drum digits **46-50 px** at 9.1-13.4:1 contrast; date lines
  20-33 px; HR 18-34 px; steps 17-24 px. **No data element outside the safe area in any
  image.** No generator claims were taken on trust — every number was re-measured.
- Drift control passed: the baseline control reproduced 4 of 5 dimensions; the date
  dimension had drifted because the earlier reviewer measured against the plate *average*
  instead of the local background (rubric §0.3 forbids the average). The correction moved
  scores upward only and did not change any verdict.
- **The gap that matters:** the drum family scores only **2-4 on the new wow criteria** —
  zero sparks, no cog train with visible tooth engagement. Readability is solved; the
  Victorian-industrial *machine* is not there yet. That is exactly what round 2 explores.

## Actionable fixes carried into Phase B (from the round-1 review)
1. Add the mechanism layer to any drum-family finalist: a riveted belt run with a ruled
   tick scale + plate offset + lit roller edge, a 3-cog train with teeth overlapping in
   phase, and 2-5 additive sparks — all >=8 px clear of the digit boxes. In that family the
   digit clear zones are y114-172 (time), y188-208 (date), y234-262 (HR/steps), so the belt
   belongs below y326 and the lowest cog tooth at y<=106.
2. Lift the drums from time 9 to 10: get the window gloss band off the digit field (cap
   interior gloss) so the drum behind the strokes stays <= (20,20,20), taking the HOUR
   window from ~9-10:1 to >=12.5:1.
3. Grow every unit/label from **7 px to 10 px** cap height and recolour from the dim
   brown (~3:1) to ivory (~13:1) — BPM, STEPS and the SEP. One code change, +2 points on
   HR and steps per image.

## Strongest bases for Phase B
- `iter_001_drum-openwork-hhmm.png` — closest to the user's Devon Tread 1 north star.
- `iter_003_verdigris-panel.png` — highest measured readability total (34/40), but a flat
  instrument panel rather than a machine.
- `iter_009_aged-ivory-panel.png` — largest digits (55 px), least contrast headroom.

## Engine (`steampunk_lib.py`)
v1 primitives plus a v2 layer added for the enhanced brief: `fit_cap` / `ink_height` /
`lining_figures` (exact digit sizing), `drum_window` (guaranteed-size drum with ghost
numerals), `plate3d` / `recess` / `crystal` (real 3D depth), `gear_layer` (lit, shaded cogs
— not flat clip-art), `belt_run` (segmented belt with tick scale and rollers),
`riveted_rail`, `knurled_crown`, `spark` (additive flare), `verify_clearance`.

Lessons encoded in the engine:
- Fit digit size on **digit ink height**, not nominal cap — most installed serif faces use
  old-style figures (3,4,5,7,9 descend), so `8,342` at a 24 px cap renders 38 px.
  Only `times_bd` has lining figures.
- PIL's `MinFilter` accepts only odd kernels >= 3; `MinFilter(1)` crashes the interpreter.
- Use **`/c/Python314/python.exe`** — the bare `python` on PATH is a broken shim (exit 127).

## Reference
`reference/devon_tread1_steampunk.png` — Devon Tread 1 Steampunk: rectangular case,
riveted brass rails, open-work mechanism behind glass, white-on-black drum digits with
engraved letterspaced brass labels, ruled belt tick scales. The user's style north star.
