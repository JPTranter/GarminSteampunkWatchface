# source: https://simmer3d.com/2020/07/23/knurl-mesh-in-blender/

# Blender Tutorial: Knurl Mesh – Simmer3D
URL: https://simmer3d.com/2020/07/23/knurl-mesh-in-blender/
Published: 2020-07-24
Author: Simmer65

Blender Tutorial: Knurl Mesh – Simmer3D

Posted on July 23, 2020 July 28, 2020 by Simmer65

# Blender Tutorial: Knurl Mesh

Knobs have knurls. A knurl is that hatch pattern found on cylindrical surfaces. They are easy to create on a lathe and, believe it or not, it is easy to model in Blender. Here’s how.

These instructions are for Blender 2.8

Start with a cylinder. Shift-A, Mesh, Cylinder

Set the cylinder parameters to a radius of 1 with a depth of 2 and 60 vertices. Select nothing for Cap Fill.

Now hit Tab to go into Edit mode. Hover your mouse pointer over the cylinder and type Ctrl-R. Type 24 (for 24 loop cuts). Left Click to finalize the 24 loop cuts and the right click to keep the loop cuts centered.

Now we want to un-subdivide. Hit “3” (not on the number pad) to go into Face Mode. Hit “A” to select all the faces. Right click to bring up the menu and click “Un-subdivide”. In the properties panel, change the iterations to 1.

Now extrude the faces by clicking Alt-E and selecting “Individual Faces”. Now move the mouse to move the faces out away from the surface.

Change the “Transform pivot point” to individual origins. Type “S” to scale and the move the mouse to shrink the faces.

You’re done.

If you want to change the depth of the knurl, change the pivot point to median. Hit “S” for scale and “Shift-Z” to scale while holding the Z constant. This is assuming your cylinder axis still follows the Z-Axis.