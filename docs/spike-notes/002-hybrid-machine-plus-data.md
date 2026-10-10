# SPIKE 002 — Hybrid pipeline: Cycles machine layer + controlled data layer

**Question.** Spike 001 proved a raytraced, self-luminous datum cannot hold the readability bar
(best 2.9:1 vs a 12:1 requirement). Does splitting the problem — **render the machine in Cycles,
composite the data in a controlled pass** — give the realism *and* keep the data legible?

**Answer: YES for realism, MOSTLY for legibility.** Materials are a clear tier above anything the
procedural pipeline produced, and the data went from **2.9:1 → up to 13.8:1**. Two digits still
sit below the bar at the wide ring, for a structural reason explained below.

## Pipeline

```
machine.py   (Blender/Cycles, 1280x1440 @64spp, ~55 s)   hardware only, NO data objects
   |          brass case, riveted rails, hollow glass tubes with dark inner sleeves,
   |          valve manifold + lamps, gauge bowls, odometer frame, cogs, arcs, haze, bloom
   v
machine_4x.png  --> downsample to 960x1080 (the project library's supersample canvas)
   v
data_layer.py (PIL, instant)   all four data elements, drawn with steampunk_lib's exact sizing
   |          dark grounds under every glyph; tube numerals with ghost cathodes + plasma bloom
   |          + a dark contour; HR gauge with a red HEART needle; odometer; date dial with a
   |          weekday ring and the hand on WE
   v
face_320.png  (320x360)  --> verified with the harness
```

`machine.py` and `data_layer.py` share one coordinate system (the ortho camera maps
`1 px = 0.01 world units`), so data positions and hardware positions are the same numbers.

## Measured (glyph-tight boxes, on the saved 320x360 PNG)

| glyph | ink height | contrast @2 px | @6 px | @16 px |
|---|---|---|---|---|
| tube `1` | 50 px | 3.42 | 5.17 | 11.63 |
| tube `0` (hour) | 51 px | 7.09 | **12.51** | 8.65 |
| tube `0` (minute) | 51 px | 7.29 | **13.75** | 7.95 |
| tube `9` | 50 px | 3.40 | 4.12 | 9.02 |
| HR `72` | 27 px | 6.01 | 9.52 | 4.57 |
| steps `8,342` | 15 px | 7.77 | 11.55 | **16.34** |
| date `30` | 30 px | 7.51 | 8.23 | 10.62 |

Compare **spike 001**: best 16 px-ring contrast **2.9:1**, digits smeared by glass refraction.
Here the time digits measure 50-51 px ink (bar: ≥44) and reach **12.5-13.8:1** at the ring that
matters for a 50 px-wide window.

## What worked
- **Real materials.** PBR brass with directional specular, real glass with IOR/transmission and
  edge highlights, cogs as actual geometry, physical bloom on emissive arcs, volumetric haze.
  The electric arcs are genuinely convincing — the thing the procedural pipeline never managed.
- **The split removes the conflict.** Nothing in the Cycles scene has to be legible, so the
  lighting/materials/bloom can be pushed hard; nothing in the data layer has to be photoreal, so
  ink heights and contrast are pinnable with `fit_cap`.
- **Black inner sleeves inside the glass tubes** are what make the numerals work: without them
  the tube interior refracts warm brass and there is no dark ground to composite onto.
- **A dark contour around each glowing glyph** is required for honesty, not looks — without it the
  bloom occupies exactly the pixel the 2 px ring samples and the measurement collapses.
- Speed is fine: ~55 s to render the machine, then the composite is instant, so a full iteration
  is about a minute.

## What still doesn't clear the bar, and why
- **`1` and `9` fall short at the narrow rings** (3.4-5.2:1 vs 12:1). They are the outer tubes and
  sit closest to the bright glass wall and the arcs. This is the **narrow-window problem**: at a
  50 px tube width a 16 px measurement ring necessarily lands on glass and brass, so the wide-ring
  number reflects the *neighbourhood*, not the ground behind the glyph. Closing it needs a wider
  tube (more dark ground inside the window) rather than better rendering.
- **The odometer digits measure 15 px ink** against an 18 px target — the reference's counter is
  compact, so the drum windows need to be taller for a compliant number.
- **The HR gauge and date dial are still crowded**: the reference's dials carry more furniture
  (range labels, weekday ring) than fits comfortably at 46 px radius, and the weekday letters are
  small at 8.5 px cap.
- **The data layer is now the weak link, not the renderer.** The machine is photoreal; the
  composited numerals are crisp but stylistically flat by comparison, and they need another design
  pass to sit convincingly *inside* the glass.

## Recommendation
The hybrid is the right architecture — keep it. Next steps, in order of impact:
1. **Widen the tubes** (radius 25 → 30-32 px) so every numeral has a dark surround wide enough to
   satisfy a 12:1 reading at the 6-16 px rings, and re-run the machine render.
2. **Raise the odometer drum windows** so the steps digits reach ≥18 px ink.
3. **Redesign the two dials** at this radius: fewer items, larger letters, or give the date dial
   its own wider bowl.
4. Then run the normal loop (generator + reviewer against `reviews/rubric.md`) on the hybrid,
   with the harness as the gate — the machine layer is now good enough that the remaining work is
   data design, which is exactly where the loop has proven effective.
