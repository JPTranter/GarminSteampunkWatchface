# TECHNIQUES — Blender/Cycles instrument build for the nixie watch face

Scope: the three round instruments + the mechanical counter in
`reference/nixie_moodboard_arcs.png`:

* **Left gauge** — clock dial, brass bezel, glass cover, heart-shaped red needle,
  blue→dark tick arc top-left, numerals 12 / 40 / 180 / 82.
* **Right gauge** — date/day dial, engraved lettering `OO MC 6I FO AW` around the
  rim, blue `61` arc, needle, numerals 24 / 7 / 11 / 00.
* **Centre** — 5-drum mechanical counter reading `12350`, brass frame.

Target build environment: **Blender 4.5 LTS**, Cycles. All parameters below are
for 4.5 unless stated; 5.x differences are flagged where they matter.

Every claim is tagged with a source URL. Items that are working practice with no
published number are marked **UNVERIFIED**.

---

## 0. Cross-cutting: modelling "turned" brass and pivots in 4.5

Two primitives underpin every instrument, so settle them first.

**Lathe / turned brass (bezel, boss, drum frame).**
Recommended: model a **profile curve** (a single open edge-loop in the XZ plane)
and revolve it. Blender's Spin tool is the classic route: profile in front view,
3D cursor on the axis, `Spin` with **Steps = 10–64, Angle = 360°**, then
`Merge by Distance` to weld the seam (`docs.blender.org/manual/en/latest/modeling/meshes/tools/spin.html`).
The **Screw modifier** is the parametric alternative — set `Screw = 0`, place the
profile so one end sits on the object origin, `View Steps` / `Render Steps` for
density, enable `Merge` (`blenderartists.org/t/blender-5-1-spin-tool/1639181`).
Pitfall: Spin is destructive and its parameters can't be re-edited after use
(same thread); Screw destroys the flat plane of a cross-section if the profile
already has faces — delete the face first, keep only edges.

**Pivot for anything that rotates (needle, drums).**
The object origin *is* the pivot. Put the 3D cursor at the dial centre and use
`Object ▸ Set Origin ▸ Origin to 3D Cursor`, or parent the mesh to an Empty
placed at the centre and rotate the Empty
(`docs.blender.org/manual/en/latest/animation/constraints/relationship/pivot.html`).
Pitfall: an Empty's "origin" is really just its Location — an Empty parented in
the wrong place rotates children about the Empty's *location*, and moving the
Empty moves the children (`blender.stackexchange.com/questions/32931/set-pivot-point-of-empty-object`).

---

## 1. The gauge / dial instrument — bezel, glass, dial face

### 1a. Bezel — turned brass ring

**Recommended approach.** Build it as real geometry, never a texture.
1. Draw the bezel cross-section as a profile line (outer wall, chamfer, inner
   shoulder where the glass sits).
2. Revolve with Spin (Steps 48–64, Angle 360°) then merge doubles
   (`.../tools/spin.html`).
3. Add a **Bevel modifier**, `Width` = 0.2–0.5 % of bezel diameter, `Segments` = 2,
   `Limit Method = Angle 30°`. The bevel exists to catch a specular line — see §6.
4. Shade smooth with a **Smooth by Angle** modifier, angle 30°.

**Material.** Principled BSDF, `Metallic = 1.0`. Brass measured F0 (linear) from
Autodesk's OpenPBR reference: **brass (0.962, 0.713, 0.464)**, F82 edge tint
(0.971, 0.994, 1.019); gold F0 (1.000, 0.735, 0.353), copper (0.932, 0.623, 0.522)
(`help.autodesk.com/cloudhelp/ENU/AR-Core/files/ac-shading/ac-surface-shaders/ac-openpbr-surface/arnold_user_guide_ac_openpbr_base_html.html`).
For a Base Color float on a 0–1 picker, Roblox's PBR table gives brass
`metalness 1.0, roughness 0.25` (polished) up to 0.48 (aged), and "pure metals
(gold/silver/bronze) roughness 0.2–0.3"
(`github.com/Roblox/creator-docs/.../material-reference.md`).
For machining marks, add **anisotropy**: Principled `Anisotropic ≈ 0.5–1.0`,
`Anisotropic Rotation 0.0` for a circumferential brushed look, `Tangent` node in
**Radial** mode (Object space) so highlights streak around the ring
(`blenderartists.org/t/how-to-make-this-watchmaking-metal-finish-perlage/1330478`,
`youtube.com/watch?v=HWt1uA1pLrI`). Note the Principled quirk: the anisotropy
direction is rotated 90° vs the Glossy BSDF, so **add 0.25 to the rotation** to
line up (`docs.blender.org/manual/en/latest/render/shader_nodes/shader/metallic.html`
and CarlG in the perlage thread above).

**Alternative.** Screw modifier (non-destructive) — see §0.

**Pitfall.** Do not scale the object in Object Mode before adding Bevel/Solidify:
the modifier multiplies by the un-applied scale factor and the bevel comes out
wrong. `Ctrl+A ▸ Scale` first (`cookstation.blog/blender-glitching-small-scale-fix`).

### 1b. Glass cover — separate object, own material

**Recommended approach: yes, separate geometry with its own material.** Model the
crystal as its own lens (a revolved shallow dome or a flat slab with a bevel),
seated on the bezel shoulder — never merged into the bezel, because the glass
needs its own IOR and thickness and the dial must be visible *through* it.

**Material.** Principled BSDF with `Transmission Weight = 1.0`, `IOR = 1.5`
(glass; manual states 1.5 is a good approximation —
`docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html`;
see also the dedicated Glass BSDF page
`docs.blender.org/manual/en/5.2/render/shader_nodes/shader/glass.html`).
Thin watch cover → reduce thickness or enable **Thin Wall**. Sapphire watch
crystals measure **IOR 2.42** if you want the crispier look
(`renato.design/formatter-app/materials/gemstone/mat_gem_sapphire_natural.html`).
Set `Roughness` 0.0–0.05 for a clean crystal.

**Pitfall — caustics noise.** Both the manual and the Wikibooks glass tutorial
warn that a bare Glass/Transmission shader throws caustic noise; the fix is to
add a **Transparent BSDF** to shadow rays (via a Light Path node) rather than
letting the transmission shader handle shadows
(`docs.blender.org/manual/en/5.2/.../glass.html`;
`en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Advanced_Tutorials/Cycles_Glass`;
`blender.stackexchange.com/questions/152739/how-do-i-make-my-glasses-look-realistic`).
Also verify `Filter Glossy` and `No Caustics` in the render settings
(`docs.blender.org/manual/nb/4.5/render/cycles/optimizations/reducing_noise.html`).

**Alternative.** "Uber glass" build (dispersion + raylength absorption + fake
caustics) if the crystal must read as thick vintage glass; already catalogued in
`hybrid/research/uber_glass_shader.md`
(`creativeshrimp.com/uber-glass-shader-blender.html`).

### 1c. Dial face — dark textured

**Recommended approach: procedural, not an image, for this project.** The dial is
small and dark; you can't see micro-structure, only a matte sheen. Use a
Principled BSDF, `Metallic = 0`, `Base Color` near-black (value ≈ 0.02–0.05),
`Roughness` 0.6–0.8, and drive Roughness/Bump with a **Noise Texture**
(Scale ≈ 200–400, Detail 2–4, Roughness 0.5) through a Bump node (`Distance`
≈ 0.001–0.005). Add fine **concentric** machining rings by feeding
`Texture Coordinate ▸ Object` → Separate XYZ → `Math ▸ Length` of (X,Y) into a
`Wave` texture (Bands, Sine) and on into the Bump node. This mirrors the perlage
/ brushed-dial node setups the Blender Artists community converged on
(`blenderartists.org/t/how-to-make-this-watchmaking-metal-finish-perlage/1330478`,
`blenderartists.org/t/procedural-brushed-metal-shader-help/678876`).

**Alternative — generated image texture.** If you want a *painted* dial (aged
paper, printed numbers), author it in Inkscape/Photoshop and UV-unwrap the disk
with a straightforward **Project from View (Front)** unwrap so the art maps 1:1;
the Stack Exchange knob answer exports the UV map as a template, paints the
numbers onto it, and re-imports as an sRGB Base Color + a separate non-colour
bump map (`blender.stackexchange.com/questions/169944/placing-text-on-a-curved-surface-in-360-degrees`).

**Alternative — markings as real geometry.** Gives the strongest specular
response and is preferred when a marking must catch light (the engraved weekday
ring, §4). Costly at these sizes; not needed on a dark dial.

**Pitfall.** Unwrapping a flat disk with `Cylinder Project` or sphere projection
smears the centre. Use Project-from-View (Front) for a flat dial.

---

## 2. Graduated scale — ticks and the two-tone blue arc

### 2a. The tick ring

**Recommended approach: a polar array of small real boxes.** One tick is a cube
scaled to roughly *0.4 % of dial diameter* wide × *2 % long* × *0.4 % tall*, with
a Bevel modifier `Width` ≈ 10 % of tick width, `Segments = 2` (this bevel is what
makes the tick read at small resolution — §6).

Now array it. **Critical 4.5 fact:** the Blender **4.5 Array modifier has no
`Circle` shape.** Its options are `Fit Type` (Fit Curve / Fit Length / Fixed
Count), `Relative Offset` Factor X/Y/Z, `Constant Offset` Distance X/Y/Z, and
`Object Offset` — plus Merge
(`docs.blender.org/manual/en/4.5/modeling/modifiers/generate/array.html`). The
**Circle shape with Radius / Sweep Angle / Angular Distance / Full-or-Arc** only
exists in the 5.x manual
(`docs.blender.org/manual/en/latest/modeling/modifiers/generate/array.html`).

So in 4.5 do the classic **Object-Offset polar array**:
1. Add an **Empty** at the dial centre.
2. Array modifier on the tick: `Fit Type = Fixed Count`, `Count = 60` (6° apart),
   `Relative Offset = (0,0,0)`, **`Object Offset` = the Empty**.
3. Rotate the Empty **Z = 360/Count = 6°**. The array now fans around the dial.
4. Requirement: apply transforms (`Ctrl+A ▸ All Transforms`) on both the tick and
   the Empty *before* assigning the modifier, or each copy compounds the mismatch
   and the array explodes outward
   (`blender.stackexchange.com/questions/186497/how-can-i-make-a-polar-array`).

**Alternative — curve-based (also works in 4.5, and gives per-tick spacing along
an arc).** Add a **Circle/Bezier circle**, give the tick an Array modifier
(`Fixed Count`, `Relative Offset X = 1.0`) then a **Curve modifier** targeting the
circle; the curve must sit **below** the array in the stack. Set the tick and
curve origins to the same point and apply transforms, or the first copy lands
offset (`blender.stackexchange.com/questions/55664/creating-knob-dial-with-indicator-strip/55750`
uses exactly Count 36 + relative offset 1.5 + a Bezier circle as curve modifier;
see also `youtube.com/watch?v=lRK8UMudejg`). Include extra geometry / subdivisions
on the tick so it bends smoothly, and raise the curve's **Resolution U** before
bending (`blenderartists.org/t/making-a-circle-follow-a-curve/565005`).

**Alternative — curve bevel.** For a *ring of tick marks generated as one object*,
use a Curve with a rectangle bevel, or the Geometry-Nodes repeat-zone approach
demonstrated for an odometer face, which places labels/ticks at the vertices of a
**Polygon-type Arc curve with Resolution 0** — one vertex per tick, index-driven —
so no manual positioning is needed
(`reddit.com/r/blender/comments/1p01u4o/odometerstyle_weigh_scale_panel_with_geometry/`).

**Pitfall.** Curve modifier blow-ups: if a point on the curve has a non-1 Mean
Radius (because the curve was scaled in Object Mode), the bevel/array diameter is
multiplied by it. Apply transforms, then in Edit Mode set `Mean Radius = 1`
(`blenderartists.org/t/making-a-circle-follow-a-curve/565005`).

### 2b. Two-tone arc (blue fading to dark)

The reference arc is a thin band *under* the ticks: bright blue at the low end,
fading to near-black toward the high end, and it glows.

**Recommended approach: separate arc mesh + Color Ramp along the arc.**
1. Build the arc as a flat annulus-sector mesh (inner radius = tick-ring inner
   edge, outer = tick-ring outer edge), spanning the gauge's sweep only.
2. UV-unwrap it as a plain rectangle with **Follow Active Quads** so **U runs
   along the arc's angular direction, V across its width**.
3. Material: `UV ▸ Separate XYZ ▸ X` → **Color Ramp** → Principled `Base Color`,
   *and* the same ramp → `Emission Color` with `Emission Strength ≈ 1–3`.
   Ramp stops: pos 0.0 = blue (linear ≈ 0.05, 0.30, 0.90), pos 0.4 = dim blue,
   pos 0.55–1.0 = near-black; interpolation `Linear` for the fade, `Constant` if
   you want banded segments. The Color Ramp maps 0→left stop, 1→right stop
   (`docs.blender.org/manual/en/latest/editors/texture_node/types/converter/color_ramp.html`).
4. Emission strength and exact blue are **UNVERIFIED** (artistic); the reference's
   glow is a raised-brightness arc, not a documented value.

**Alternative — angular gradient without UVs.** Feed `Texture Coordinate ▸ Object`
→ Separate XYZ; compute θ = `arctan2(Y, X)` with Math nodes and map through the
Color Ramp, or drop a **Gradient Texture** set to `Radial` on Object coordinates
and rotate it with a Mapping node to sit the blue segment where you want it
(`blender.stackexchange.com/questions/72169/how-do-i-assign-a-color-ramp-to-a-360-axis`;
a combined radial+length polar setup is in
`blender.stackexchange.com/questions/269928/how-to-add-multiple-gradient-from-different-angles`).

**Pitfall.** Radial gradients band. If banding shows, switch the ramp
interpolation to `Linear`/`Ease` and raise the gradient's resolution, or bake a
small gradient image instead.

---

## 3. The needle — heart-shaped head on a tapered shaft

### 3a. Tapered shaft

**Recommended approach:** a 6–8-sided cylinder scaled to a long taper, or a
Bezier curve with a very small bevel and a **Taper Object** on the curve to
narrow it toward the tip (`docs.blender.org/manual/en/latest/modeling/texts/properties.html`
documents the shared Taper Object mechanism). Add a Bevel modifier for a specular
edge. Taper the *shaft*, keep the *head* a separate joined piece so you can
control both.

### 3b. Heart profile — four credible routes

**Recommended: parametric heart via a curve, then extrude.**
- The classic parametric heart (used widely in Blender threads) is
  `x = 16 sin³t`, `y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t` (the standard
  "heart curve" — `note.com/mim2026/n/n1f47d8a4919d`).
- In Blender: `Add ▸ Mesh ▸ Math Function ▸ XYZ Math Surface` with
  **X = sin(u)^3**, **Y = 0**, **Z = (13*cos(u) − 5*cos(2u) − 2*cos(3u) − cos(4u))/16**,
  `U min 0`, `U max 2π`, `U wrap` on, `V min = V max = 0`, `V step 1` — this
  produces the closed heart outline. Then `Ctrl+V ▸ Dissolve Vertices` (remove
  doubles), `E` extrude + `Esc`, `S 0.025` to inset the extruded ring, `F` to
  face-cap. That is the exact recipe from
  `blender.stackexchange.com/questions/63697/how-can-i-generate-an-object-from-a-mathematical-function`
  (requires the Add Mesh: Extra Objects addon).

**Alternative — Bezier curve by hand.** `Add ▸ Curve ▸ Bezier Circle`, then in
Edit Mode select the top and bottom handles and press `V` (Vector), pull the
top handle up and the left/right vertices up until it reads as a heart; set
`Extrude > 0`, then `Bevel Depth` + `Bevel Resolution` for rounded edges, and
`Alt+C` to convert to mesh
(`blenderartists.org/t/beginner-a-simple-3-heart/438548`). Blender Studio's 4.5
fundamentals exercise uses the same approach and stresses keeping handle lengths
equal for symmetry
(`studio.blender.org/training/blender-fundamentals-45-lts/blender_4-5_lts_creating-curves`).

**Alternative — SVG import.** Draw the heart in Inkscape, save as SVG, import;
it arrives as an editable Bezier curve, then use `Extrude`/`Bevel` in Object Data
Properties or a Solidify modifier for thickness
(`katsbits.com/codex/shape-key-animation`).

**Alternative — bmesh from the parametric equation.** Spawn verts along `t` in a
loop and build the face; full example in the SE thread above.

**Pitfall (all routes).** Bezier hearts are notoriously asymmetric unless the
left/right handle lengths match; the parametric and SVG routes are symmetric by
construction. After extruding inward (`S` small, or `Extrude Faces Along
Normals` with a negative factor) recalculate normals with `Shift+N`, or the
underside shades black.

### 3c. Red metal needle + centre boss + pivoting to a value

**Material.** Red metal = Principled BSDF with `Metallic = 1.0`, `Base Color` a
deep red, `Roughness` 0.2–0.35 (anodised/aluminium-red range per the Roblox
table's "painted/coloured metal ≈ 0.3",
`github.com/Roblox/creator-docs/.../material-reference.md`); red metal F0 is not
published in the tables consulted → **UNVERIFIED**.

**Centre boss.** A small revolved brass cap (Spin, Steps 24, 360°) sitting over
the needle pivot so the needle appears to rotate beneath it. Keep it a separate
object.

**Pivoting / rotating to a value.**
- Put the needle's **origin at the pivot** (§0). Rotate with `R Z <angle>`.
- To drive it from a value: add a **Custom Property** on the needle or a driver
  object, then a **driver** on the needle's Z-rotation with expression
  `radians(angle_per_unit * value)`. Blender drivers work in **radians** —
  `blender.stackexchange.com/questions/166078/advanced-rotation-animations`
  (batFINGER: "Blender uses radians") and the odometer/driver threads below.
- A gauge sweep of e.g. 270° for full scale is a design choice; the exact degrees
  in the reference are **UNVERIFIED** — measure from `07_arcs_detail.png`.

**Pitfall.** If you use a Quaternion or Axis-Angle rotation mode, drivers and
constraints behave unexpectedly; set `Rotation Mode = XYZ Euler` on anything
driven (`blender.stackexchange.com/questions/55664/.../55750`).

---

## 4. Engraved lettering around a ring — `MO TU WE TH FR SA SU`

"Engraved" here means cut *into* the brass, with a bevelled lip that catches
light — not printed on top.

### 4a. Getting the letters onto the circle

**Recommended approach: Text object → Curve modifier → convert → engrave.**
1. `Add ▸ Text`, set the font (a large serif — Trajan/Garamond-class), type the
   days, set `Horizontal Align = Center`, `Vertical Align = Center`.
2. Add a **Circle curve** at the ring radius. Raise the circle's `Resolution U`
   so the bend is smooth.
3. Add a **Curve modifier** to the text, target = the circle, `Deform Axis = X`
   (experiment with X/Y/Z; the axis you want is the one that runs along the
   curve). The manual explicitly recommends the Curve modifier over the legacy
   "Text on Curve" field for control
   (`docs.blender.org/manual/en/latest/modeling/texts/properties.html`).
4. Tab into the circle in Edit Mode and `Ctrl+T` to **tilt** the curve so the
   letters lie flat on the ring face rather than standing on edge; if the text
   comes out upside-down, use `Segments ▸ Switch Direction` on the curve.
5. Add **Solidify**, then a **Remesh** modifier in **Sharp** mode with `Octree
   Depth` raised until the bent letters stop glitching — Remesh must sit
   **between** Solidify and Curve so it cleans the mesh before the bend
   (`blender.stackexchange.com/questions/169944/placing-text-on-a-curved-surface-in-360-degrees`).
6. `Object ▸ Convert ▸ Mesh` (or Mesh from Curve/Met/Surf/Text).

**Alternative — Shrinkwrap + Lattice (keeps the text editable).** Extrude the
text, add a **Lattice** with one subdivision on the wrap axis, place it so it
barely overlaps the back of the text, give the **text** a Lattice modifier (target
= lattice), and give the **lattice** a Shrinkwrap modifier targeting the ring
cylinder. Deforming the lattice wraps the text around the surface, and the text
stays live (`blender.stackexchange.com/questions/44758/emboss-text-onto-curved-surface`).
The same thread warns that smooth embossing is hard and lists three options:
separate extruded text object; model into the mesh; or a greyscale displacement
map + subsurf (`Level 5–7` for a perfect surface).

**Alternative — Simple Deform (Bend).** Convert text to mesh, `X ▸ Limited
Dissolve` to clean the messy converted topology, add **Simple Deform / Bend**
(90° on Z, or whatever matches the arc) and place in front of a higher-vertex
cylinder (`blender.stackexchange.com/questions/289335/how-can-i-engrave-this-text-on-the-side-of-this-cylinder`).

### 4b. Making it read as ENGRAVED

**Recommended approach: model the recess as real geometry, then knife/flip.**
- After the letters are bent and converted, **Knife Project** them onto the ring
  mesh (`Mesh ▸ Knife Project` in Edit Mode, with the letters as the knife
  object, `Cut Through` enabled), so the ring now carries letter-shaped faces
  flush with its surface (`.../questions/289335/...` and
  `.../questions/237078/is-there-any-way-to-fix-the-awful-topology-on-curved-text`).
- Select those faces and `Mesh ▸ Extrude Faces Along Normals` with a **negative
  factor** to push them *into* the metal — this is the step the SE knob answer
  calls out explicitly: *"Extrude Faces Along Normals to push the text faces in
  the knob and get the engraved look"*
  (`blender.stackexchange.com/questions/169944/...`).
- Depth: engrave **0.15–0.4 mm on a 40 mm ring** (i.e. ~0.4–1 % of diameter) so the
  wall is visible but the floor isn't lost — **UNVERIFIED**, tune visually.
- Bevel the cut edges slightly (`Width` ≈ 10–20 % of the engraved depth, 1–2
  segments) so the top lip catches a highlight. This is the whole trick: an
  engraved letter reads because a *bevel line* brightens, not because the letter
  is dark.

**Boolean alternative.** Text → Extrude → Convert → **Decimate (Planar)** to clean
topology → **Shrinkwrap** (Project, negative) onto a *duplicate* cylinder → Solidify
→ **Boolean Difference** on the visible cylinder. Critical: shrinkwrap onto
`Cylinder1` and boolean-cut `Cylinder2` — wrapping and cutting the *same* surface
creates a dependency loop and letters stop engraving partway round
(`blender.stackexchange.com/questions/346569/engraving-text-on-curved-surface`).

**Texture/normal-map alternative (cheapest, and often enough at watch scale).**
Export the UV layout as a template, paint the letters black-on-grey in Inkscape,
and use the greyscale as a **non-colour Bump** (and/or Displacement) input; the
community answer notes this "saves you a lot of heavy geometry" and, for Cycles,
you can enable **Adaptive Subdivision** and just lower the `Dicing Scale`
(`blender.stackexchange.com/questions/169944/...`). Also from
`.../questions/44758/...`: a greyscale displacement map + subsurf is the third
canonical route. Note the practical caveat in
`.../questions/311087/engraving-text-into-surface`: for pure *look*, **bump map**
is the recommended answer ("you're unlikely ever to see the profile").

**Pitfall.** Converted text topology is "usually a bit messy" — the manual's own
tip is to run `Limited Dissolve` or a low-threshold **Remesh** to clean it
(`docs.blender.org/manual/en/latest/modeling/texts/editing.html`). If you skip
this, the Curve modifier shreds the letters.

---

## 5. The mechanical counter — five digit drums in a brass frame

### 5a. Modelling the drums

**Recommended approach:** five cylinders, each ~12–16 sides, radius ≈ drum
height/2.6, with a **Bevel modifier** on the rim (`Width` = 5 % of drum radius)
and two thin flange rings (smaller cylinders) at each end to form the brass
frame. Keep each drum a **separate object** so it can rotate independently. Shade
smooth with a Smooth-by-Angle modifier.

### 5b. Getting digits to read as printed on the curved drum

Three routes, in order of fidelity:

**Recommended — UV-map the drum and place digit images.**
1. Mark the vertical band seams, `U` unwrap the cylinder so you get one rectangle
   0–1 in U around the circumference.
2. Make a long strip texture: digits `0 1 2 3 4 5 6 7 8 9` laid out along U (one
   rotation's worth of faces), white on a dark drum colour, with the drum's brass
   edge bands left plain. The Evil Martians walkthrough does exactly this for a
   phone-picker cylinder and stresses using a **monospaced font** so every digit
   occupies the same arc width (`evilmartians.com/chronicles/blend-to-my-will-fonts-on-cylinder-objects-in-blender.md`).
3. If you prefer real 3D digits, add a Text object per digit, curve/shape it onto
   the drum, then parent/duplicate it around the axis using an **Empty at the
   drum centre** and rotate duplicates by 360/10° — "In Blender, Null can be your
   best friend" for exactly this (`evilmartians.com`, same article).

**Alternative — Shrinkwrap + Knife Project for raised digits.** Same workflow as
§4: convert digits to mesh, `Decimate (Planar)`, **Shrinkwrap (Project, negative)**
onto the drum, `Solidify`, then Knife Project and extrude *outward* slightly so
the digits stand proud of the drum (they're printed, not engraved, on a real
counter) (`blender.stackexchange.com/questions/346569/...` and
`blender.stackexchange.com/questions/169944/...`).

**Alternative — Bump/normal only.** Greyscale digit strip as a non-colour Bump
input; adequate if drums stay a few dozen pixels tall.

**Drum shading / specular.** The drum should read as **dark, slightly glossy
painted metal**: Principled `Metallic 0`, `Base Color` value ≈ 0.02–0.05,
`Roughness` ≈ 0.35–0.5 so a soft vertical specular band rolls over the curve —
the specular band is what sells "cylinder" (`github.com/Roblox/creator-docs/.../material-reference.md`
gives glossy plastic 0.1 / matte plastic 0.4 as the general neighbourhood). The
metallic is in the **frame**, not the drums.

**Pitfall.** If you UV-unwrap a cylinder with `Cylinder Project`, the seam and the
cap smearing wreck the digit strip; unwrap with marked seams instead (also the
warning in `blender.stackexchange.com/questions/275015/how-to-add-text-or-texturize-it-on-a-curve`).

### 5c. Rigging the wheels to rotate (noted, though we render static)

The established pattern is **drivers with integer floor-division**, chained so
each drum is driven by the previous one:
- Give each drum a **Custom Property** `unit`, clamped 0–9; put a driver on its
  X-rotation with expression `2π * unit / 10` (`6.28 * unit / 10`).
- Give the scene a `count` property and drive each drum's `unit`:
  units `count % 10`, tens `floor(count % 100 / 10)`, hundreds `floor(count / 100)`,
  and so on; then keyframe only `count`
  (`blenderartists.org/t/physical-counter-system-rotation-according-to-variables/601792`).
- The stepping/"sudden shift" comes from the **`//` floor-division operator** in
  the driver expression — the SE answer uses
  `pi * ((180.0 * yrot / pi) // 40 * 10) / 180.0` to advance the next dial 10°
  for every 40° of the previous, and notes the same formula chains to any number
  of dials (`blender.stackexchange.com/questions/1491/how-to-rig-a-rotary-counter`).
- A ready-made animatable odometer uses a single "initial reading" property on the
  case object driving the drums' X-rotation via a small Python driver
  (`blendswap.com/blend/20093`) — a useful reference file to read.

**Pitfall.** Drivers are in **radians**; and any driven object must be in XYZ
Euler rotation mode (`.../questions/166078/...`, `.../questions/55664/.../55750`).

---

## 6. Reading well at small size (final render a few hundred px)

This is the section that decides whether the instruments survive at watch scale.

1. **Set the pixel filter deliberately.** Render Properties ▸ Film ▸ Pixel Filter.
   Cycles default is **Blackman-Harris** and `Filter Width` **1.5 px**; lower
   values give crisper edges. For a small render, try `Width 0.8–1.0` with
   Blackman-Harris. A bare `Box` filter at 1.0 is sharp but aliased
   (`docs.blender.org/manual/en/4.5/render/cycles/render_settings/film.html`;
   the 1.5 default and 0.01–10 range are in
   `docs.blender.org/api/2.74/bpy.types.CyclesRenderSettings.html`;
   practical guidance in `brainbound.blog/antialiasing-blender-guide` and
   `yelzkizi.org/how-to-make-blender-render-higher-quality/`).

2. **Render oversize, then downsample.** This is the single biggest win.
   A very well-answered SE case renders a 192×192 image and finds it far softer
   than rendering at 512×512 and downscaling in an external tool: *"if I render it
   at 192×192 directly in Blender, the image is far far softer"* — the fix is to
   render at 2×–4× and resize down with a good filter
   (`blender.stackexchange.com/questions/280307/rendering-at-small-resolutions-cause-unexpected-softness-lack-of-sharpness`).
   That thread also notes Eevee's anti-alias jitter is defined in *pixels*, so
   changing output resolution changes the effective AA.

3. **Watch the denoiser.** OpenImageDenoise actively erases detail smaller than
   about a pixel; the fix is to *raise the render resolution*, or turn denoising
   off and rely on many samples. Reported: fine bump detail was "wiped out almost
   completely" at 200 % resolution but survived at 400 %
   (`blenderartists.org/t/how-to-denoise-in-3-0-to-remain-fine-bump-details/1334858`).
   The manual likewise recommends feeding the denoiser at least the Albedo pass,
   and warns `None` "can blur out details, especially at lower sample counts"
   (`docs.blender.org/manual/en/4.5/render/cycles/render_settings/sampling.html`).

4. **Sample settings.** Enable `Noise Threshold` (adaptive sampling); the manual
   quotes typical thresholds **0.1 → 0.001**, lower = better/longer. A value of 0
   makes Cycles auto-pick. Set `Min Samples` if you need a floor before adaptive
   kicks in (`docs.blender.org/manual/en/4.5/render/cycles/render_settings/sampling.html`).
   Also enable the **Light Tree** and use the **Denoise** pass
   (`.../sampling.html`, and the noise-reduction page
   `docs.blender.org/manual/nb/4.5/render/cycles/optimizations/reducing_noise.html`).

5. **Give detail something to catch.** Geometry far smaller than a pixel
   disappears into the average; a slightly **oversized bevel** on a tick, needle
   edge or engraved letter lip produces a bright specular *line* that survives
   downsampling much better than a dark groove. This is standard practice and the
   rationale behind the bevel widths in §1a/§2a/§4b — the specific "≈2 px minimum
   feature size" rule of thumb is **UNVERIFIED** (no published number found), so
   validate against your actual output resolution.

6. **Don't over-model.** Because §2/§4 geometry is duplicated dozens of times,
   keep tick/letter meshes low-poly (a bevel with `Segments = 2`, a Remesh octree
   depth no higher than the render can resolve). Extra sub-pixel geometry only
   costs render time and aliasing.

---

## 7. Minimum viable recipe — one line per area

| Area | Minimum viable recipe |
|---|---|
| **1. Gauge** | Profile curve → Spin (Steps 48, 360°) → merge doubles → Bevel 0.2–0.5 % dia, Seg 2 → Principled `Metallic 1.0`, Base Color brass (0.962, 0.713, 0.464), Roughness 0.25. Glass = **separate object**, Principled `Transmission 1.0`, `IOR 1.5`, add a Transparent-BSDF shadow fix. Dial = near-black Principled + Noise (Scale 300, Detail 3) → Bump (Distance 0.003) → concentric rings from `Length(X,Y)` → Wave. |
| **2. Ticks + arc** | Tick = scaled cube + Bevel 10 % width, Seg 2. Array `Fixed Count 60` + **Object Offset = Empty at centre**, Empty rotated 6° (4.5 has **no Circle array shape**). Arc = flat annulus-sector, Follow-Active-Quads UV, `UV.X` → Color Ramp (blue → near-black) → Base Color + Emission (Strength 1–3). |
| **3. Needle** | Shaft = tapered 6–8-sided cylinder or curve + Taper Object. Head = parametric heart `X=sin(u)^3, Z=(13cosu−5cos2u−2cos3u−cos4u)/16, U wrap`, extrude + `S 0.025` + `F`. Material red metal `Metallic 1.0`, Roughness 0.3. Origin at dial centre; rotate on `Z`; drive via Custom Property + driver in **radians**. Brass boss spun on top. |
| **4. Engraved lettering** | Text + Curve modifier onto a tilted (`Ctrl+T`) Circle → Solidify → Remesh (Sharp, raise Octree) → Convert to Mesh → Knife Project onto ring → `Extrude Faces Along Normals` **negative** (depth ~0.4–1 % dia) → small bevel on the lip. Boolean alternative: shrinkwrap onto Cylinder1, cut Cylinder2. Cheap alternative: greyscale → Bump, non-colour. |
| **5. Counter** | 5 cylinders (12–16 sides) + Bevel; separate objects; dark glossy drums (`Metallic 0`, Roughness ≈ 0.4). Digits = UV strip unwrapped with marked seams (monospaced font), or Shrinkwrap+Knife-Project raised digits. Rotation: Custom Property `unit` 0–9 → driver `2π·unit/10`; scene `count` → `count%10`, `floor(count%100/10)`, `floor(count/100)`; XYZ Euler only. |
| **6. Small-size legibility** | Pixel Filter **Blackman-Harris, Width 0.8–1.0**; render at **2–4×** and downsample (biggest win); set `Noise Threshold 0.01–0.05`, enable Light Tree + Denoise(Albedo+Normal); if denoise eats detail, raise resolution or disable it; oversized bevels so edges read as specular lines. |

---

## Sources

- Array Modifier — Blender **4.5** LTS Manual: https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/array.html
- Array Modifier — Blender latest (**5.2**, has Circle shape): https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/array.html
- Polar array / Object Offset: https://blender.stackexchange.com/questions/186497/how-can-i-make-a-polar-array
- Knob dial with indicator strip (Count 36, rel. offset 1.5, curve modifier): https://blender.stackexchange.com/questions/55664/creating-knob-dial-with-indicator-strip/55750
- Array along a curve (order of modifiers): https://youtube.com/watch?v=lRK8UMudejg
- Circle following a curve / Mean Radius fix: https://blenderartists.org/t/making-a-circle-follow-a-curve/565005
- Text on curved surface, 360° (bend + engrave, full recipe): https://blender.stackexchange.com/questions/169944/placing-text-on-a-curved-surface-in-360-degrees
- Emboss/engrave text on curved surface (3 methods; lattice+shrinkwrap): https://blender.stackexchange.com/questions/44758/emboss-text-onto-curved-surface
- Engrave text on a cylinder (Shrinkwrap + Boolean, dependency loop): https://blender.stackexchange.com/questions/346569/engraving-text-on-curved-surface
- Engrave text on cylinder side (Limited Dissolve + Simple Deform Bend): https://blender.stackexchange.com/questions/289335/how-can-i-engrave-this-text-on-the-side-of-this-cylinder
- Fixing topology on curved text (Limited Dissolve + Knife Project): https://blender.stackexchange.com/questions/237078/is-there-any-way-to-fix-the-awful-topology-on-curved-text
- Engraving text into surface (bump-map is the recommended answer): https://blender.stackexchange.com/questions/311087/engraving-text-into-surface
- Text Properties (Text on Curve vs Curve modifier; Taper): https://docs.blender.org/manual/en/latest/modeling/texts/properties.html
- Editing Text Objects (messy topology; Limited Dissolve / Remesh): https://docs.blender.org/manual/en/latest/modeling/texts/editing.html
- Text Introduction (convert to mesh/curve): https://docs.blender.org/manual/en/latest/modeling/texts/introduction.html
- Math-function heart object (XYZ Math Surface recipe): https://blender.stackexchange.com/questions/63697/how-can-i-generate-an-object-from-a-mathematical-function
- Heart by Bezier (handles, extruded, bevel): https://blenderartists.org/t/beginner-a-simple-3-heart/438548
- Blender Fundamentals 4.5 — Creating Curves (heart exercise, Extrude vs Bevel): https://studio.blender.org/training/blender-fundamentals-45-lts/blender_4-5_lts_creating-curves
- SVG import as Bezier (Extrude/Bevel/Solidify): https://katsbits.com/codex/shape-key-animation
- Parametric heart equation: https://note.com/mim2026/n/n1f47d8a4919d
- Gradient along a 360° axis (Radial gradient + Object coords): https://blender.stackexchange.com/questions/72169/how-do-i-assign-a-color-ramp-to-a-360-axis
- Multiple polar gradients: https://blender.stackexchange.com/questions/269928/how-to-add-multiple-gradient-from-different-angles
- Color Ramp node reference: https://docs.blender.org/manual/en/latest/editors/texture_node/types/converter/color_ramp.html
- Digits around a cylinder (UV strip, monospaced font, Null/Empty): https://evilmartians.com/chronicles/blend-to-my-will-fonts-on-cylinder-objects-in-blender.md
- Text/UV on a curve (seams warning): https://blender.stackexchange.com/questions/275015/how-to-add-text-or-texturize-it-on-a-curve
- Odometer-style arc with Geometry Nodes repeat zone (one vertex per tick): https://www.reddit.com/r/blender/comments/1p01u4o/odometerstyle_weigh_scale_panel_with_geometry/
- Rig a rotary counter (floor-division driver): https://blender.stackexchange.com/questions/1491/how-to-rig-a-rotary-counter
- Counter system driven by variables (custom property, count%10 etc.): https://blenderartists.org/t/physical-counter-system-rotation-according-to-variables/601792
- Advanced rotation animations (drivers in radians): https://blender.stackexchange.com/questions/166078/advanced-rotation-animations
- Animatable Odometer reference file: https://blendswap.com/blend/20093
- Spin tool (lathe): https://docs.blender.org/manual/en/latest/modeling/meshes/tools/spin.html
- Screw modifier as lathe / Spin limitations: https://blenderartists.org/t/blender-5-1-spin-tool/1639181
- Pivot constraint: https://docs.blender.org/manual/en/latest/animation/constraints/relationship/pivot.html
- Empty pivot point: https://blender.stackexchange.com/questions/32931/set-pivot-point-of-empty-object
- Principled BSDF (IOR 1.5 glass, metallic, anisotropy): https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- Glass BSDF (caustics noise; transparent-for-shadows): https://docs.blender.org/manual/en/5.2/render/shader_nodes/shader/glass.html
- Glass BSDF (Japanese mirror of same text): https://docs.blender.org/manual/ja/dev/render/shader_nodes/shader/glass.html
- Cycles glass tutorial (IOR 1.45 Fresnel): https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Advanced_Tutorials/Cycles_Glass
- Realistic glass node setup (Glass+Glossy+Transparent): https://blender.stackexchange.com/questions/152739/how-do-i-make-my-glasses-look-realistic
- Metal F82/Physical-conductor tables incl. brass F0: https://help.autodesk.com/cloudhelp/ENU/AR-Core/files/ac-shading/ac-surface-shaders/ac-openpbr-surface/arnold_user_guide_ac_openpbr_base_html.html
- Metallic BSDF (aniso rotation +0.25 note; metal values): https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/metallic.html
- PBR material reference values (metals roughness 0.2–0.3; brass zipper 0.25): https://github.com/Roblox/creator-docs/blob/main/content/en-us/art/modeling/material-reference.md
- Sapphire watch crystal IOR 2.42: https://renato.design/formatter-app/materials/gemstone/mat_gem_sapphire_natural.html
- Anisotropic brass discussion: https://blenderartists.org/t/anisotropic-brass/1453500
- Perlage / radial metal finish (tangents, aniso rotation): https://blenderartists.org/t/how-to-make-this-watchmaking-metal-finish-perlage/1330478
- Procedural brushed metal shader (cylindrical/disk mapping, seams): https://blenderartists.org/t/procedural-brushed-metal-shader-help/678876
- Guilloche watch-dial pattern: https://blenderartists.org/t/help-with-guilloche-pattern-watch-dial/1390636
- Radial brushed metal (Noise scale 400, mapping Z 0, aniso rotation 0.7): https://www.youtube.com/watch?v=HWt1uA1pLrI
- Cycles Film / Pixel Filter (Blackman-Harris, width): https://docs.blender.org/manual/en/4.5/render/cycles/render_settings/film.html
- filter_width default 1.5, range 0.01–10: https://docs.blender.org/api/2.74/bpy.types.CyclesRenderSettings.html
- Cycles Sampling (Max Samples, Noise Threshold 0.1–0.001, Min Samples, denoiser passes): https://docs.blender.org/manual/en/4.5/render/cycles/render_settings/sampling.html
- Reducing noise (caustics, Filter Glossy, Light Tree, clamp): https://docs.blender.org/manual/nb/4.5/render/cycles/optimizations/reducing_noise.html
- Render at small resolution → softness; fix by rendering oversize + downsampling: https://blender.stackexchange.com/questions/280307/rendering-at-small-resolutions-cause-unexpected-softness-lack-of-sharpness
- Denoiser wipes fine detail below ~1 px; raise resolution: https://blenderartists.org/t/how-to-denoise-in-3-0-to-remain-fine-bump-details/1334858
- Antialiasing / pixel filter guidance: https://brainbound.blog/antialiasing-blender-guide
- Render quality / filter width guidance: https://yelzkizi.org/how-to-make-blender-render-higher-quality/
- Apply scale before Bevel/Solidify (small-object precision): https://cookstation.blog/blender-glitching-small-scale-fix
- Advanced glass shader (uber glass): https://www.creativeshrimp.com/uber-glass-shader-blender.html
- Companion research in this repo: `hybrid/research/{anisotropic_brass,uber_glass_shader,knurl_mesh,nixie_tube_modelling,volume_scatter}.md`
