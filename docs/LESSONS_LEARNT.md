# LESSONS LEARNT — Steampunk watch face (Garmin Venu Sq 2), iterations 001-070

Scope: a generative design loop that produced 60 approved 320x360 faces, two Blender rendering
spikes, and a component-first 3D rebuild. The point of this document is that the *process*
lessons are worth more than the artwork. Numbers are the real measured ones from this project.

---

## 1. Process: what actually made the loop work

**L1. Separate the creator from the verifier, and make the verifier re-measure.**
The generator's self-reported numbers ran optimistic on every single round: claimed needle and
hand deltas of exactly `0.00°` measured 2.4° and 3.5°; claimed `17.6:1` chart contrast measured
`14.2:1`; claimed "the ≥6 px bright run is confined to fork junctions" measured 23-37 such rows.
None changed a verdict, but none could be trusted either. The reviewer re-measuring the saved
image — never reading the generator's log — is what kept the project honest.

**L2. Freeze the bar before rendering, and forbid moving goalposts.**
Write the numeric pass condition into the spec *before* the batch exists, and put anti-goalpost
rules in the rubric: no new criterion may gate a verdict unless it was published earlier; a newly
noticed issue is a NOTE that gates only from the *following* round; re-score the previous best as
a drift control every round. Without this an LLM reviewer quietly raises the bar forever and the
loop never converges.

**L3. Two phases, opposite standards.**
*Concept sweep*: rough, fast, high variance — and rough edges must NOT be polished, because the
only question is "is this idea cool?". *Form finalists*: polish and exact numbers, and only here
can something be approved. Applying finish quality to a concept wastes the budget; letting a
sketch through the finish gate wrecks the bar.

**L4. A reviewer can and should reject everything.**
`REJECT_ALL` — declare a whole family dead and demand a fresh organising idea — is a necessary
verdict. Without it the loop optimises a bad idea forever.

**L5. Assemble the deliverable from curated picks, not from "the last thing rendered".**
Yes, keep a ledger (iterations spent, per-round outcome, best-of-batch, fixes carried forward),
but also curate at the end.

---

## 2. Measurement: the lessons that cost the most time

**L6. Measure the datum, not its container.**
A box spanning a whole nixie tube returned `ink_height = 145 px` for a 51 px digit, because the
threshold mask caught the bright glass wall instead of the glyph. Sanity check: **if several
different regions return an identical ink height, the box is too big.** Use a tight box per glyph.
This mistake was made twice, in two different pipelines.

**L7. Never measure contrast against a region average** — use the surface immediately behind the
stroke (a ring outside the ink mask), and **always state the ring radius**. The same artifact
reads ~2 points different between a 2 px and a 16 px ring. Two reviewers disagreed about a
baseline purely because one sampled the plate average and the other the local background.

**L8. A bounding box that carries glow/bloom padding is the wrong object for a clearance test.**
A bbox-to-bbox "4.9 px collision" measured ≥10 px ink-to-ink, and a claimed "0.0 px" screw
collision did not reproduce at all — the real distance was 52 px. Measure nearest ink pixel.

**L9. Watch for measurement-gaming, and add a wide-ring control.**
A per-stroke halo lifted exactly the pixels the ring test samples (14.2:1 at 2 px vs 12.9:1 at
16 px). Requiring the same artifact to clear the bar at a wide ring is what makes the number mean
something. If it passes anyway, the halo is cosmetic noise, not a cheat.

**L10. Optical criteria must be judged optically.**
A mandatory "≥6 px bright core" turned electric arcs into fat 13-16 px columns instead of thin
branching bolts. The numeric proxy destroyed the intent it was written to protect. State optical
criteria as optical, judge with crops at 4-10x, and keep numeric proxies out of the gate.

**L11. Fit text size on the ink height of the glyphs actually present, not on a nominal cap.**
Most serif faces use *old-style figures* (3,4,5,7,9 descend; 6,8 ascend), so `8,342` at a nominal
24 px cap rendered 38 px. Only Times Bold had lining figures among the installed set. Probe for it.

---

## 3. Blender / headless: every one of these cost a failed render

**L12. `--background` loads Blender's default startup scene** (Cube + Camera + Light). The default
Cube enclosed the test scene and rendered as a flat grey slab. Always
`bpy.ops.wm.read_factory_settings(use_empty=True)` first.

**L13. Blender resolves a relative render filepath against its own CWD, not the script's** — it
wrote to `C:\probe_out.png` and failed with "Permission denied". Use absolute output paths.

**L14. The screen vertical is world Z, and view depth is world Y.** Rotating a cylinder 90° about
X to "lay it down" makes its length run *into* the screen, producing a 150 px deep solid glass rod
that swallowed the digits. Tubes take the default Z axis; only camera-facing discs take `axis='Y'`.

**L15. Smaller y is nearer the camera.** Emissive digits placed at y=+0.06 sat *inside* the solid
box of the plate meant to carry them, so the plate occluded its own data. Print each object's
`front_y` in a layer self-check.

**L16. A nixie tube must be a hollow shell, and a single-sided shell reads as SOLID glass.**
Open cylinder + Solidify; and apply scale first or thickness/IOR/volume absorption all mis-scale.

**L17. A crashed interpreter loses buffered stdout.** A native crash (PIL's `MinFilter` accepts only
odd kernels ≥3 — `MinFilter(1)` kills the process) showed as a silent non-zero exit with no output.
Run unknown scripts with `-u`, and log to a file rather than reading a pipe.

**L18. Log to a file and grep it. Blender's stdout is enormous.** Piping it through `head` silently
truncated the very lines I needed (my own layer self-check) while pages of "Synchronizing object"
went past. Write to a log, grep for your own markers.

---

## 4. The central finding: photorealism fights legibility

**L19. A self-luminous datum cannot hold a contrast bar in a photoreal render environment.**
All-in-Cycles measured a best of **2.9:1** against a 12:1 requirement, in both tone-mapping
regimes: AgX compresses emissive glyphs to grey, Standard clips them to white where their own
bloom then floods the frame. And a glyph behind curved glass is smeared by refraction however it
is lit. This is physics, not a bug.

**L20. Split the problem: render the machine photoreal, composite the data, gate with the harness.**
Cycles renders hardware with no data objects in the scene; the numerals are composited in a
controlled pass. Time digits went **2.9:1 → 12.5-13.8:1** at the 6 px ring. The weak link moved
from the renderer to the data design — which is exactly where the generator/reviewer loop works.

**L21. Two techniques made the composite work, and both are honesty mechanisms, not decoration.**
A **dark inner sleeve** inside the glass tube (without it the interior refracts warm brass and
there is no dark ground to composite onto), and a **dark contour around each glowing glyph**
(without it the bloom occupies precisely the pixel the 2 px ring samples).

**L22. Read reference images carefully, and let the user correct you.** A mood board reading
`1248` was a real 12:48 time, a real step counter and a real day number — a layout *blueprint*,
not decoration. Misreading it as noise cost a whole round of material variations, and the two
best ideas in the project (the weekday-ring date dial, the odometer counter) came from the user's
correction.

---

## 5. Research

**L23. Prefer written technical sources; video pages extract to nothing.** Blender Stack Exchange,
Blender Artists threads with node screenshots, and the official manual produced concrete parameter
values. YouTube pages produced 2 KB of boilerplate.

**L24. The thing you were told exists may not.** "Render the sparks through a Blender plug-in" —
verified against the Extensions platform *and its JSON API*, the installed build (14 bundled
add-ons, none electrical/VFX), and the paid market: **no good add-on exists**; the market sells
Geometry-Nodes node groups. Verification cost minutes and saved an unknown amount of flailing.

**L25. Verify against the actual install, not memory.** The researcher's own recollection said Cell
Fracture ships with Blender; inspecting the build showed it does not (it moved to Extensions after
4.1).

**L26. Tell researchers to mark UNVERIFIED rather than fill gaps.** Every guide produced came back
with an explicit list: no canonical emission strength for a discharge (published examples span
3-100), the brass base colour interpolated from Blender's copper/gold conductors, cm-scale volume
density derived rather than published. Those lists are more useful than fake precision.

---

## 6. Time and token efficiency (what to change next time)

**L27. Parameterise attempts; never rewrite the scene.** The component runner took a JSON parameter
block (`{"ring_steps":2,"knurl":0,"lamps":3,...}`), so a variation was a data edit rather than a
30 KB script rewrite. This is the single biggest time saver in the whole 3D phase.

**L28. Store every attempt and build progress sheets.** 23 saved tube attempts plus A/B sheets let
one vision call judge a whole progression. **Judging N images in one contact sheet instead of N
separate vision calls is the biggest token saver available.**

**L29. Give children documents to READ, not text to parse.** Pasting the full technique guide into
a task prompt costs thousands of tokens per child; writing it once to disk and telling the
child to read that file costs ~20.

**L30. Have the creator run its own verification and self-check before the verifier sees anything.**
The cheapest defect is the one caught in the same agent, in the same context, without a round trip.

**L31. Numbers in the return schema, not prose.** Require printed measurements in a structured
field so the orchestrator can compare rounds mechanically instead of reading paragraphs.

**L32. Do one render per component, not one render of everything.** Component-first makes each
judgement tractable, keeps failures isolated, and lets the pieces be validated in parallel or
sequentially without one broken part contaminating the review of another.

**L33. Delegate the context-heavy work.** Rule-of-thumb from this project: long design loops,
literature/technique research, and independent verification are all worth delegating; quick
parameter checks, one-shot renders and anything needing the user's eye are not.

**L34. Kill a broken direction early.** Two steers ("the glass is milky", "the silhouette is a bell,
not a drawn nipple") after 20 attempts saved the remaining 30 from chasing the wrong target.
Reviewing a child's in-flight output is cheaper than letting it finish.

---

## 7. What I would do differently

1. **Build the measurement harness before the first render**, not after the first false number.
2. **Write the rubric and freeze the bar before any artifact exists** — here it needed a mid-loop
   correction because the target moved, and the honest handling of that (NOTE now, gate later) was
   more work than doing it up front.
3. **Ask the user to confirm the reading of every reference image** at intake. One question would
   have saved a round.
4. **Go component-first from the start.** Rendering the whole face repeatedly to fix one part
   wastes the most expensive resource (render time) and the hardest to manage (attention).
5. **Test the raytracer's *data* legibility before investing in its *materials*.** The spike would
   have been 20 minutes instead of an hour if the first test had been "can a glowing digit be read
   in this environment" rather than "does brass look like brass".

---

## 8. The Connect IQ phase — a watch face on real hardware

The finished design was re-implemented as a watch face in Monkey C for a Venu Sq 2 Music
(320×360 AMOLED). Different platform, same lesson as §2 and §4: **the numbers that decide the
layout are the ones the device itself reports.**

**L35. A bitmap font cannot be scaled at runtime, so every size the layout needs is its own font
resource.** The layout wanted 53 px tube digits, 32 px gauge digits, 29 px for the heart rate,
23 px for the odometer drums and 11 px labels, against a device whose *smallest* built-in font is
39 px. Five font resources — and each one is a separate atlas in memory. Decide the sizes once, from
measurements, because adding a size later means adding a resource.

**L36. Fit a font size on measured ink, not on the point size, and fit it to the container's clear
interior, not to the grid pitch.** Ink height came out at ≈ 0.67 × the point size (old-style serif
figures): 76→53 px, 48→32, 43→29, 34→23. And the drums are pitched 19 px apart but only have ~28 px
of clear dark inside the window — so the 32 px digit that "fitted the layout" spilled onto the brass
frame, and the fix was a shorter font, not a smaller number.

**L37. A glow on a Garmin is solid pixels, and the core must out-shine its own halo.** `drawText`
has no alpha and a bitmap font cannot be blurred, so a bloom can only be painted as offsets of the
same glyph in dimmer colours — far ring first, then the near ring, then the core. The first attempt
used a mid-blue core and it dissolved into the glow; the user caught it immediately ("the font within
the glow should be brighter/whiter so it is not blurred into the glow"). **The halo carries the
colour; the core carries the contrast.**

**L38. Declaring a resource and generating it are one change.** `fonts.xml` was committed listing
`NixieMid` before `make_fonts.py` had ever written `NixieMid.fnt`, so the tree as committed could not
build. Generate, then declare, in the same commit — or the next person's first build fails for a
reason that has nothing to do with their change.

**L39. Read the simulator's own status bar instead of reasoning about the memory budget.** The CIQ
simulator window reports a used/limit kB figure (123.9 kB here, i.e. the device's watch-face limit)
and it sat at 10.2 kB with five fonts and a 64-colour full-screen background loaded. What that number
does and does not count is **UNVERIFIED** — it is not obviously additive with the `w*h*bpp/8` rule
that says the background alone is 86 KB — so treat it as a liveness/trend indicator, not a budget
audit. (The build failing is what actually tells you a resource set is too big.)

**L40. Screenshotting the simulator: grab the window, and do not try to infer the screen rectangle.**
`ImageGrab` can only see what is on top of a screen rectangle, and `SetForegroundWindow` is refused
for a background process — the first capture was a web browser that happened to sit over the
simulator's rectangle. `PrintWindow` (with `PW_RENDERFULLCONTENT`) makes the window draw itself into
a memory DC and needs no focus, which fixed the capture. **The crop did not get fixed by anything.**
The device screen is not findable by brightness: the case's black bezel, the artwork's own black
bands, the simulator's dark toolbar/status bar and the window's black non-client regions are all
`rgb(0,0,0)`, and a warm-pixel (brass) match latches onto window chrome. Three automatic
calibrations — dark-region bbox, brass-silhouette matching, warm-row density band — each returned a
wrong rectangle, and a wrong crop is worse than no crop because it looks like a rendering bug. The
crop is now an explicit `--crop x0,y0,x1,y1`, checked against a 320:360 aspect sanity test.

**L41. Three commands are worth more than the steps they save here.** The loop "change a constant →
build → push → look → ship" is what this phase actually consists of, so it got three tools:
`ciq/preview.py` composites the frame offline from the view's *own parsed constants* (no drift, no
build — a layout tweak in a second), `ciq/simshot.py` builds, pushes and captures the simulator in
one command, and `ciq/push_watch.ps1` sideloads to the real watch and proves the copy by reading it
back and comparing SHA-256. The preview is the fast loop; the simulator and the watch stay the source
of truth — a preview that disagrees with the device is a bug in the preview.

**L41b. A Garmin watch is an MTP device, not a disk.** There is no drive letter, so `cp` and
shell-by-path do not work; the copy has to go through the shell's namespace
(`Shell.Application` → *This PC* → the device → `Internal Storage\GARMIN\APPS`) via PowerShell. And
MTP copies report success without guaranteeing anything, so the push script reads the file back and
compares hashes. Also: **a watch that drops MTP leaves a USB device Windows can no longer bind to** —
`Get-PnpDevice -Class WPD` still lists it while *This PC* does not, and the fix is to unplug and
replug, not to retry the copy.

**L42. `monkeydo` is slow and blocking, not broken — do not read "still running" as a hang.** It
needs the simulator already running (with none it queues instead of erroring), and a push has been
observed to take anywhere from ~50 s to several minutes while it waits on the simulator, *after which
it returns 0*. The lesson is about the diagnosis, not the tool: the first push was watched to a
268 s "hang", killed, and the push actually succeeded — the same command, left alone, exited cleanly.
If a command's job is "push a file and wait", give it minutes and a generous timeout, and confirm the
outcome from the artifact (here: the simulator rendering the new build), never from how long it took.
Wrapping it in a short timeout is exactly what discards a successful push.

**L43. Push a dial's text against the ring, not against the neighbouring line.** "Lower the weekday
and the day slightly" is a *radial* move inside a round dial: what has to stay clear is the dial's
rim at the top and the month at the bottom, so the check is the ink-to-rim gap at each row, not the
line spacing. (The same class of error as L8 — measuring the wrong object.)

**L44. DECISION — split-scale layout, candidate C (user-approved).** The face was too small: the
uniform width-fit (0.3365) kept the whole device on screen. A uniform scale cannot enlarge it much,
because the dial *centres* sit near the art's edges (x 207 / 813), so above ~0.38 a readout leaves
the screen before the tubes fill the width. The fix was to scale the halves independently —
**tubes + manifold at 0.49, dials + counter at 0.43** — joined across the dark gap under the
manifold (source y 506) with an 8 px feather, which shows no seam. The user was shown three
mockups (`ciq/artwork/zoom/_zoom_compare.png`: uniform 0.38, split 0.46/0.40, split 0.49/0.43) and
chose C, plus **removing the heart-rate dial's winged pointer** (inpainted out of the dial face in
`prepare_artwork.py`). Cost accepted: the tubes are larger relative to the dials than in the art,
the outer sparks and side pipes are cropped, the tube tips touch the top edge. Digit ink went
53→75 (time), 29→37 (HR), 32→42 (day), 23→29 (steps). The general form: when one transform cannot
satisfy two regions, split the transform at a seam the art already hides, rather than compromising
both. Carry the text coordinates as *source-grid* points (the old shipped values mapped back), so
hand nudges survive a rescale.

**L45. A preview that has never been compared to the device has bugs you have stopped seeing.**
`preview.py` shipped with two: it read a stale `resources/images/background.png` (brown watermark
patch) instead of the drawable the build uses, and it passed `0xRRGGBB` ints straight to PIL, which
reads a bare int as `0xBBGGRR` — so the blue glow rendered orange and the ivory text blue, in every
preview since it was written. Both were caught only by looking at it next to a change. Point a
preview at the exact file the build packages, and convert colours explicitly.

**L46. DECISION — the AMOLED needs warm tones pre-corrected, and the compiler owns the palette.**
Two findings, both measured:
1. *The panel shifts brass to copper.* In one photo holding both the monitor (simulator) and the
   watch, the same brass read hue 28° on the monitor and 17° on the watch, G/R 0.69 vs 0.54, and
   slightly more saturated. The simulator capture matched the source exactly (31°), so the build was
   right and the shift is the panel. `device_colour.py` rotates warm hues +11° and trims their
   saturation ×0.9 before the build, weighted to warm hues only (the blue glow and lamps measured
   unchanged). On a monitor the result looks yellow-green — that is the pre-compensation. A
   four-strip calibration build (`make_calibration.py`: +0/+6/+11/+16°) was sideloaded, and the
   user confirmed the corrected face "looks good on the actual watch".
2. *Our palette reduction was pointless and harmful.* `automaticPalette` defaults to TRUE on 16-bit
   devices, so the compiler reduces any bitmap to ≤256 colours itself: 64-colour, 256-colour and
   full-colour PNGs compiled to .prg files within 0.4 % of each other. The 64-colour PNG only threw
   away colours — it was the posterised tube glass. With `automaticPalette="false"` the bitmap is
   true 16-bit (.prg +114 KB, which is exactly the 8→16 bpp difference) and it loads and renders on
   the watch: bitmaps live in the graphics pool, not the 128 KB app heap, so the earlier "must
   palette-reduce to fit 128 KB" reasoning (from `w*h*bpp/8` arithmetic) was wrong. Read what the
   compiler does before doing its job for it, and measure the artifact (.prg size) to see what it
   actually stored.

**L47. A verify step can fail in ways that look like the thing it verifies failing.**
`push_watch.ps1` had three bugs, all of which reported a broken push on pushes that worked:
an em-dash inside a string broke Windows PowerShell 5.1's parse of the whole file (it reads
BOM-less UTF-8 as ANSI, and the dash's last byte is a curly quote in cp1252 — keep `.ps1` strings
ASCII); the readback looked for a renamed file, but Shell `CopyHere` keeps the source name; and when
overwriting an earlier build, "the file is present" is true at once — it is the *old* file — so a
single readback compared the previous build's hash. The script now reads back into its own folder
and retries until the hash matches. The independent check that exposed each one was hashing the
read-back file by hand.

**L48. DECISION — the date goes into the dial's ring (user-approved: the 54 px version of
`ciq/artwork/date_ring/_compare.png`).** Weekday and month are set one letter per segment of the
date dial's outer ring, rotated to it; the day number alone fills the inner disc (42 → 53 px ink).
Two things made it work. *Measure the art's own divisions, do not assume a grid:* the ring's 12
dividers are hand-drawn and 25–36° apart, and an automatic peak-pick mislocated three of them —
reading the dividers off a polar unwrap of the dial was what put each letter inside its segment.
*Pre-render what the device cannot draw:* `drawText` has no angle, so the 19 words are opaque
patches of the shipping background with the letters blended in — no bitmap alpha needed, compiled
16-bit like the background so no palette edge shows, loaded once a day rather than per frame.

**L49. The glow pulse was invisible because the swing was relative to a dark colour.** 78–100 % of
the halo's dark blues moved them a few levels, and a fresh random target every frame read as noise.
What made it visible was an absolute-looking swing (35–120 %), *holding* each level for a few frames
and easing toward it, and an instant flash on strike that fades. Judge an animation parameter by
the colour it acts on, on the target screen — not by the percentage.

**L50. DECISION — heart rate as a zone gauge, variant B (user-approved: row B of
`ciq/artwork/hr_gauge/_compare.png`).** BPM is gone; a band round the HR dial runs cold blue →
green → orange → red and is lit up to the current rate, dim beyond. Each of the user's five zones
(`UserProfile.getHeartRateZones`, which needs the `UserProfile` permission) gets an equal fifth of
the arc, as Garmin's own zone gauges do — so the colours sit at fixed angles for every user and
the dim band can be *baked into the background*; the watch draws only the lit part, one `drawArc`
per 5° segment from a generated colour table. Put live-drawn colours through the same AMOLED
correction as the baked ones (both come from `hr_gauge.py`), or the lit and dim halves of one
band disagree on the panel. The arc opens to the screen edge because the dial's centre is 29 px
from it. Below zone 1 (a resting rate) nothing is lit — so the preview's mock HR is now 128.

**L51. Tooling for cheap iterations: one command per stage, one line per result.**
`ciq/make.py` runs the asset chain in its dependency order (artwork → corrected background with
the baked gauge → gauge table → date-ring patches → fonts), builds every product with a size +
sha256 line each, previews, and pushes with verification — printing full output only on failure.
Rules that keep a change cheap:
- Change a constant → `make.py preview` (seconds). Only `make.py push` when it should be on the
  wrist; only `simshot.py` when the simulator is genuinely needed (monkeydo takes minutes, L42).
- Generated files (`DateRing.mc`, `HrGauge.mc`, the ring patches, the fonts) are rebuilt by
  `make.py assets`; never hand-edit them, never re-read them to "check" — read the generator.
- Compiler intermediates (`external-mir/`, `internal-mir/`) are untracked: each build rewrote
  ~2,000 lines of them into every diff.
- Commit with explicit paths (`git add -A -- <paths>`) and check `git diff --cached --name-status`
  first. A chained `git add -u` that fails half-way leaves files staged, and the next commit
  silently sweeps them in (it happened once here; fixed by a soft reset before anything was shared).
  The same goes for deletions staged early with `git rm`: they ride along with whichever commit
  comes next, so stage deletions in the commit they belong to, and read the staged list every time.
- Decision mockups (`zoom_candidates.py`, `date_ring_mockup.py`, `hr_gauge_mockup.py`) stay as the
  record of what was shown; the shipping code lives in the generator they led to.

**L52. The build is deterministic, so "the watch runs HEAD" is a hash comparison, not a memory.**
Two `monkeyc` builds of the same tree are byte-identical (measured), so `make.py build` on a clean
tree prints the sha256 the watch *should* hold, and `make.py push` reads the device copy back and
compares. When asked "is it on the watch?", answer from that pair of hashes; it costs two lines.
(Two builds of the same sources made an hour apart once differed by a 4-byte metadata shift with
identical pixel data, so compare against a fresh build of the current tree, not an old .prg.)

**L53. Before a repo goes public, scan the HISTORY, not the tree — then decide what history to
publish.** The working tree was clean, but `gitleaks detect` over all commits found the original
signing key (`ciq/keys/developer_key.pem`, committed before its ignore rule existed). History
also held a deleted third-party product photo (a commercial watch kept only as a style reference) and
compiler intermediates whose paths embedded the Windows username. Deleting a file does not remove it from
history, and the key being void (it was regenerated) does not make publishing it acceptable. The
user chose to publish a single fresh commit of the cleaned tree; the full private history is kept
as a backup bundle outside the repo. The gates now match eClock: gitleaks + `detect-private-key`
pre-commit hooks, a full-history gitleaks CI job that also fails if any key or build output is
tracked, belt-and-braces `.gitignore` patterns (`*.pem *.der *.key .env* *.iq /release/`), and
machine paths written as `%APPDATA%` rather than a home directory. Image metadata was checked too:
the AI images carry Microsoft's C2PA provenance (generator, timestamps), which was kept on purpose.

**L54. Generate positions from the layout; never hand-carry them.** A 5 % zoom-out touched
everything measured on the old frame: tube digits, drums, arc endpoints, the HR gauge centre and
radii, the date dial, the ring radius and the font sizes. Each was converted once from where it
was measured to the 1024 grid, and `prepare_artwork.geometry()` maps it through the current
scales into a generated `Layout.mc`. The proof that the refactor was faithful is cheap and
exact: feed the *old* layout back through `geometry()` and every hand-measured value that shipped
on it comes out unchanged. A future zoom is one line.

**L55. A gauge must read at the user's normal state, and its colours must follow their mental
model.** The zone gauge started at zone 1 (~95 bpm), so at rest it lit nothing and looked broken
on the watch (reported as "does not light up at all"). It then got a below-zone-1 part. The user
expected **green to start at 60 bpm**: colours keyed to bpm, not to zone fractions. The arc is
now seven equal parts, 40–60 (blue), 60–zone 1 (green), then the five zones. That keeps the
baked gradient fixed for every user while 60 bpm lands exactly on the blue/green boundary.

**L56. DECISION — clear blue glass tubes and Nixie One digits (user-approved; matched to a user reference image kept local-only, mockups in
`ciq/artwork/glass_digits/`).** The art's tubes read as polished brass, with saturation ~120/255
on the glass walls. Desaturating alone (mockups A–C) made them grey, not glass. What matched the
user's reference was *re-lighting*: keep luminance, cast it cool blue, push the mid-tones down for
a clear dark interior, and add the light a real envelope shows. That means a specular streak, a
faint opposite one, rim light on both walls, a hotspot under the dome, and a blue haze where the
digit lights the glass. The masks are per-tube rectangles on the 1024 grid, measured on the walls,
stopping above the collars. The time digits are now **Nixie One** (SIL OFL, `ciq/fonts-src/`):
thin and even like wire cathodes. Licensing note for a public repo: the remaining bitmap fonts
(Times New Roman Bold for the other numbers, Georgia for the ring letters) are rasterised Windows
fonts. Their redistribution is a grey area and they should move to OFL fonts too.

**L57. Rolling step belts: use the art's real geometry, clip per window, animate only awake.**
The art has five drum windows; the face used four, so counts over 9,999 lost a digit. Each window
is now a clip rectangle: the digit is drawn with its belt neighbours 30 px above and below,
showing as slivers at the window edges. A changed digit rolls down one place over six animation
ticks (ease-out), driven by the same high-power timer as the arcs, and snaps when asleep.
`preview.py` mirrors the rule frame for frame (`--anim` includes an 8,399 → 8,400 rollover).

**L58. Write multi-file edit scripts to a file; never inline them in a shell heredoc.** Three
times a heredoc-wrapped Python edit turned `"\n"` into a real newline inside a string literal,
and the edited file stopped compiling. A script written with the file tool and then run is
literal, re-runnable and reviewable, and its `assert s.count(a) == 1` per edit catches a stale
anchor before anything is half-applied.

**L59. DECISION — hot orange tubes with a honeycomb anode grid, and a thin wire for the digits
(user-approved; candidates in `ciq/artwork/tube_restyle_candidates.png`, stroke test in
`ciq/artwork/tube_restyle_stroke.png`).** The face shipped blue digits in cool glass; the user's
reference photographs were orange, so the ink, the glass and the digits' weight all moved. Every
value came from measuring the reference rather than eyeballing it: the wire is a hot yellow-white
core (`(252,226,150)`; the photo measures `(236,225,139)` at luminance 0.87) inside ONE bright
orange ring `(255,118,38)`; the glass haze went warm `(0.62,0.26,0.06)` with a warm specular; the
anode grid is a hex lattice at 16 cells across a tube. Two findings worth keeping:

- **A mesh must occlude, not glow.** Drawn additively the honeycomb *cost* digit contrast (2.8 →
  2.0 on the same core-vs-glass measure) because it added light under the glyph. Drawn as a
  multiply occluder it gave the contrast back (2.8) and reads as wire mesh rather than a printed
  pattern. Reference and readability were not in conflict here: the photo's own digit-vs-glass
  ratio is ~2.8 and the face sits in the same band.
- **Two halo rings read as "complex shading"; the reference has one.** `GLOW_RAD2 == GLOW_RAD1`
  makes `glowing()` skip the outer pass entirely — one ring, and 8 fewer glyph blits per digit per
  frame. A drawn glow is solid offsets of the glyph, so each extra ring is real per-frame cost.

Stroke weight is a FONT property, not an ink one: Nixie One's stems are ~2x the thickness of the
reference's wire, so `make_fonts.py` takes a `thin` argument (erode 1 px per side, then a 0.5 px
blur to put the anti-aliasing back). 2 px per side starts eating the vertical stem of a `1`.

**L60. DECISION — live-drawn ink is GENERATED (`source/TubeInk.mc`), because it must be
pre-corrected exactly like the baked art.** The background is pre-corrected once by
`device_colour.correct()`; the digits are drawn live by `drawText`. While the ink was blue that
mismatch did not matter — the correction's weight fades out below 340 deg and above 80 deg, so blue
and the lamps were untouched. Orange sits exactly where the AMOLED shifts, so the shipping
constants are now `device_colour.correct()` of the target colour measured off the reference, written
by `ciq/tube_colour.py` into a generated `.mc` and wired into `make.py assets` — the same pattern as
`HrGauge.mc`'s corrected segment table. Rule: a colour the watch draws live goes through the SAME
correction as the artwork, and lives in a generated file so the two cannot drift. The separator
(two solid dots in the digits' own ink, no glow ring) is drawn the same way, with its geometry
generated into `Layout.mc`.

**L61. A brightness pulse must SCALE the colour, never clamp it — clamping shifts the hue.** The
glow pulse multiplied each channel of the halo ring by 35..260 % and clamped at 255. The ring is a
saturated orange, so its red was already at 255: every pulse above 100 % clipped red and green
together and walked the glow toward yellow, worst at the strike flare (measured: 100 % (255,166,60)
→ 120 % (255,199,72) → 260 % (255,255,156), and the user saw it immediately: "when the number
becomes more bold, its colour should only change slightly — now it becomes too yellow"). The fix is
two-part: `Discharge.haloColour` caps the multiplier at 255/max-channel (so it can only brighten up
to the point where the brightest channel saturates, never past it), and the ring's stored colour
keeps HEADROOM — it is the intended peak divided by `PULSE_MAX`, so 100 % rests a step below the peak
and 120 % lands on it. Cost: the resting ring is 17 % dimmer than a ring stored at its own peak, and a
flare can no longer exceed the peak (it saturates instead). Any pulsing colour needs that headroom
designed in; a colour stored at its own maximum has nowhere to go but a hue shift.

**L62. A generated asset has to follow the ink, not the build it was first made in.** The Connect IQ
hero banner kept the blue background and blue neon title from the first (blue-ink) build, and its
face was rendered before the L61 pulse fix, so the digits still flaunted the yellow overshoot the
user had just flagged. Two rules came out of it: a banner's glow is the product's own colour (it is
generated from `preview.py`'s frame, so it can only be as up to date as the last `make.py
screenshots`), and **every regenerated asset must be re-run after a colour or pulse change**, not
just after a layout change. The store upload set is the same story - it depicts a version, so it has
to be rebuilt whenever that version's look moves.

**L63. Two looks were removed after seeing them on the frame: the moving glow, and the spark shower.**
Both were built, measured and then dropped — neither is on the face now.

- **The glow pulse is gone; the ring is a fixed bright baseline.** The halo rings breathed 35..120 %
  and flared to 260 % when an arc touched a tube. Keeping that from turning the orange yellow needed
  the whole hue-preserving cap of L61, and the user's verdict was that a glow that moves is not worth
  any of it: `tube_colour.py` now stores the ring at the colour the pulse used to reach at its peak,
  and `Discharge` carries no pulse state at all.
- **The spark shower was removed as not working.** Two versions were built: 4-13 dots with halos, then
  a 30-41 particle streak shower (one 1 px line back along each velocity + a hot head) tuned against a
  reference GIF of hundreds of motion-blurred sparks. At 320x360 the particles read as speckle over the
  brass rather than a fountain, and at the face's draw budget the reference's density is not reachable.
  A live particle effect is a poor fit for a small face whose background is already a busy artwork:
  prototype the EFFECT on the device before building the tuning machinery around it, and do not assume
  "more particles" is the missing ingredient.
- **A separator is the colour the digits READ as, not the colour one of their layers is.** The colon
  was drawn in `INK_TIME` (the digits' core) and read yellow beside orange glyphs — because a thin
  pale core inside a bright orange ring, at 3 px, reads as the RING. The dots now use `INK_GLOW1`.
- **Measure from the frame you are measuring.** Points read off the shipping frame must be inverted
  through the SHIPPING transform. Using `_unmap` (which inverts layout C, the older 0.95 zoom) put the
  spark emitters and their band 5 % off — a whole tuning pass went into a geometry error.

**L64. Readability on the device outranks the look that was chosen on the screen.** The tube digits
shipped THIN — `make_fonts.py` eroded Nixie One by 1 px per side to match a reference photograph of a
wire cathode — and the user reported them "really hard to read on the device". Measured on the
rendered frame (glyph ink plus its 1 px halo, as the eye sees it): 4.2 px stroke at 5.0:1 contrast
against the glass. Natural weight is 6.2 px at 6.2:1 and one step fatter again (`thick=1`) is 9.0 px
at 6.6:1. The eroded stroke was ~3 px of glyph at 74 px ink, and the AMOLED plus the panel's own
small-pixel behaviour washed it out — a 3 px line is not a wire at arm's length, it is a gap.

Consequences worth keeping:

- **Weight and colour are the two cheapest readability levers, and both are font/ink changes, not
  layout changes.** A reference photograph is a stand-in for taste, not a measurement of what a
  panel can show; prototype the weight on the device before adopting it.
- **The 1 px halo IS most of the digit's colour at this size.** With a 3-6 px stroke, a ring at
  radius 1 covers the outer pixels of the stroke, so the digit reads as the RING colour around a
  thin pale core — which is why "make the digits redder" was a change to `INK_GLOW1`, not to the core
  in `INK_TIME`. (Same finding as L63's separator dots, from the other direction.)
- **`thin`/`thick` are one argument each on the font generator**, so going back is a one-line change
  plus `make.py assets`, not a redesign.

**L65. Two readability fixes that were geometry and rendering, not colour.** The user asked for "at
least one more vertical pixel between the numbers of each digit on the steps count" and for the
weekday and month names on the dial ring to be bold.

- **Belt spacing is a layout constant with a readability floor.** `BELT_PITCH` was 30 px with 28 px
  digits on the belt — a 2 px gap — so the window's top and bottom edges showed a fat sliver of the
  neighbouring numeral, which reads as broken digits rather than as a belt. At 32 px the gap is 4 px
  and the window holds the numeral cleanly. The pitch is one number in `prepare_artwork.py`
  (`BELT_PITCH_SRC`), generated into `Layout.mc`, and both the view's roll animation and the preview
  read it from there.
- **Bold by STROKE, not by adding a font.** The ring's WED / SEP are Georgia glyphs rendered at a
  ~10 px cap into opaque patches; L56 already flags the rasterised Windows faces as a licensing grey
  area, so the fix was an outline on the same glyph (`stroke_width` at SS x = 0.8 px at final size)
  rather than bolting on Georgia Bold. At a 10 px cap that takes Georgia's ~1.2 px stems to ~2 px —
  the difference between a leaping word and a smudge on the wrist.

**L66. A repo video does not play in a README; a GIF does - and stabilising costs two settings.**
The store clip (7 s of the face on the wrist) came in at 484x704, 60 fps, 14.5 Mbps HEVC: 12.7 MB, of
which almost all was waste. What worked:

- **Trim first, detect second.** vidstab is two passes, and the transform file is per-frame: running
  `vidstabdetect` on the full clip while encoding from `-ss 1.2` applies every row to the wrong frame,
  and the video JUMPS. Detect on exactly what will be encoded.
- **`maxangle` is the rotation control, and it has no limit by default.** This build's
  `vidstabtransform` has no `rotational` option; unbounded `maxangle` (-1) lets it rotate the frame,
  which on a wrist shot reads as the whole picture tilting. `maxangle=0` + `optzoom=1` (static zoom,
  not the dynamic default of 2) gave wobble RMS 11.6 -> 1.5 px on rigid content at the same rotation
  as the source. `deshake` (translation only) managed 4.9 px and added rotation of its own.
- **Measure the shake on RIGID content.** Phase-correlating a crop that includes the watch display
  returns nonsense, because those pixels are supposed to change.
- **GitHub**: a committed `.mp4` referenced from a README does **not** play (the `<video>` tag is
  stripped for repo/raw URLs) - it is a download link. Inline motion means either an animated GIF
  committed to the repo (what this project does) or an `.mp4` dragged into the GitHub README editor,
  which lands on `user-attachments` and renders as a native player. The GIF is made with
  `palettegen`/`paletteuse` (340 px wide, 11 fps, 3.6 s, 160 colours -> 3.0 MB; 280 px/10 fps was
  1.9 MB). ffmpeg's APNG muxer produced 13 MB for the same clip, so it is not the smaller option here.
**L67. "The tubes look wrong - too much blue" was ONE constant, and the reference that fixed it moved
the CAST, not the haze.** The envelopes are built by `glass_tubes()` as
`base = pow(clip(lum * GLASS_CAST_RGB), GLASS_GAMMA)` - a per-channel gain that had replaced the AI
art's gold with a cool blue cast (0.78, 0.95, 1.22). Measured on the shipping frame (blue-dominant =
`B - (R+G)/2 > 12`), blue was **4.83 % of the face** and almost all of it was the glass: every tube
carried a shoulder-highlight cluster at (104,123,154), B-R +40, and the wall rims at (81,91,112),
B-R +26. The blue sparks, lamps and gauge segment are baked artwork and were never the complaint - a
per-element attribution (`blue_probe.py`: flood-filled clusters with their own mean colour, not a
bounding-box average) is what says which element to change.

- **The ladder is what makes the answer one line.** With the cast as a module constant instead of an
  array literal inside the function, five rows (current / half-blue / neutral / neutral-lighter /
  warm-neutral) render from in-memory overrides with zero residue: the neutral row dropped the blue
  pixels to **1.20 %** and left only the artwork's own sparks and the gauge.
- **Neutral was not the answer - the reference was.** The user's next image was a warm amber tube
  render, so the shipping cast is now **(1.30, 0.74, 0.26)** at gamma 1.35, landing the lit glass at
  (116,81,54), hue 26 deg against the reference's measured 27-35. Amber, not grey.
- **The BASE cast is what the panel re-lights; a warm haze cannot re-tint the envelope.** The haze
  only covers the region the element's own glow reaches, while the cast moves the whole tube - which
  is exactly why the glass looked blue while its haze and specular were already warm.
- **Every axis gets its own measured row.** The second reference moved the INK too, so ink rows
  carried (core-vs-glass ratio, stroke px) measured on the ERODED glyph core: pale cream ink 8.2:1,
  the exact reference match 6.2:1, and the shipped row 7.5:1. Matching the glass without matching the
  ink would have left a pale cream wire inside amber glass; matching the reference exactly would have
  cost the most contrast - so the core first shipped one step hotter (7.5:1 against the retained ring).
- **The user then overruled that trade on the wrist** - "the time display is not orange enough. It
  should be like the reference" - and the contrast was not the binding constraint at all: the
  reference's own core measures 6.2:1 on the glyph core at a 5 px stroke, and the panel called the
  hotter row pale. Render the rung before shipping it, but take the DIRECTION from the wrist: a device
  report is the only measurement taken from the panel side, and here it also settled that the RING
  stays bright (it is what the separator dots and the halo edge read as) while only `INK_TIME` moves.

**L68. The animated side sparks: emit from the PAINTED element's own core, fly the way the user says,
and mirror the RNG in the device's exact order.** The user asked for the artwork's blue side sparks to
be animated.

- **The emitter is a measurement.** It is the bright core of the spark the artwork already paints:
  the top-15 % blue-excess centroid in each side margin, (10,138) left and (306,135) right, inverted
  through the **shipping** transform (`_src_from_screen`, never the legacy `_unmap`) and generated
  into `source/Layout.mc` as `SPARK_X` / `SPARK_Y`. The round-trip proved the transform: the
  generated constants came back as exactly those screen pixels.
- **Direction came from the user, and the first prototype had it wrong.** Radiating outward into the
  screen corner looked nothing like the artwork; the requirement is that the filaments fly **up**
  beside the tubes - "the emitter on the side where the current blue spark emitter is ... fly off into
  the area above the emitter beside the tubes". A fan about straight up with a small outward bias
  (`SPARK_UP -90`, `SPARK_BIAS -13/+13`, spread 32 deg, length 22-70 px) is that sentence.
- **Reuse the palette of the phenomenon that already exists.** The sparks use the bolts' own
  bloom/sheath/core (`0x2F6EA8 / 0x7AB6F7 / 0xEAF6FF`), which is also what the reference's sparks
  measure (core (149,191,233), tips (11,20,37)). A new effect that is the same physical thing as an
  existing one does not need a new palette.
- **One animation owner.** The sparks live in `Discharge` with the arcs - one state machine, one
  timer, one `reset()` path - and the offline mirror in `preview.py` consumes the LCG in exactly the
  device's order (degree, length, bend, tip jitter, per filament, per pass). A mirror that draws the
  right thing but consumes randoms in a different order replays *different frames*, and that looks
  like a tuning bug rather than a mirror bug.
- **Lifecycle unchanged**: 2 emitters x 10 filaments x 3 pen passes, drawn only while a burst is on,
  and only while the timer runs (high power, ~10 s after a wrist raise). Nothing animates in low power.
**L69. "It does not have a glowing orange effect" is a complaint about the FALLOFF, not the colour - and
a bloom has to follow the lit strokes.** After the ink was already the reference's own orange, the user
still read the digits as flat: the missing thing was the way light leaves the wire.

- **Measure the reference's radial profile, not its colour.** `ciq/ref_glow.py` masks the ink (bright,
  saturated, warm), dilates it in steps and reports the median colour/luminance of each ring around it:
  the reference sits at L111 at 0.5 of ITS px (the wire's own halo), L32 at 1.2, L21 at 2.3, L15 at
  4.0, L11 at 6.8 and L3 at 11.4 - and its tube is ~164 px across against our 60, so divide those
  distances by ~2.9 to get ours. That single measurement separates the two things a "glow" is made of:
  a TIGHT bloom hugging the wire and a broad haze in the glass.
- **The enemy was the haze, not the ink.** Our glass held L17-23 all the way out to 11 px - a wash that
  fills the tube. Narrowing it (sigma 48x85 -> 20x60 source px) and adding painted bands reproduced
  the reference's falloff (L26 / L16 / L12 / L11) and the digits started to read as glowing. A tube
  that is lit everywhere is a tube with nothing glowing in it.
- **A one-pixel ring cannot make a bloom, and baking one does not work either.** `drawText` has no
  alpha, so a live glow is solid offsets of the glyph - the falloff can only be STEPS (radius 1/2/3
  with three colours, 8r glyph blits per digit per frame each, so 1/2/3 costs 48 where one ring cost
  8). The baked alternative was tried and measured: a union of all ten glyphs at the shipping size,
  blurred, added to the glass - ten digits overlap so heavily that the union is a filled BLOB of the
  digit box (L61 at 2 px where the reference is at 21-32), because a bloom has to follow the strokes
  that are actually lit and those change every minute. Delete the dead knob when the bake loses.
- **Judge it at 4x as well as at 1x.** Stepped bands can read as a blocky outline; at 4x the chosen
  ladder showed a continuous halo, visible only because the bands are 1 px each and the glyph's shape
  dominates. Cheap to check, and it is the difference between shipping a glow and shipping a border.
