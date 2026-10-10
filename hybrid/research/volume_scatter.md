# source: https://blenderdiplom.com/en/tutorials/all-tutorials/582-cycles-volume-scatter.html

# Tutorial: Cycles Volume Scatter Explained
URL: https://blenderdiplom.com/en/tutorials/all-tutorials/582-cycles-volume-scatter.html
Author: Frederik Steinmetz

Tutorial: Cycles Volume Scatter Explained

Volume Scatter in Blender Cycles De-Mystified Featured

Volume scattering is used to create effects like smoke, dust, clouds, sun beams (a.k.a. god rays) and similar things. This tutorial will help you understand everything about volume scatter in Cycles and how to get the effects you expect from it.

When light passes through certain objects, it may seem as if the light itself is actually visible. A great example of this effect is a very dusty room with sunlight streaming in from a window. Similar to how the light from that window reflects off all of the tiny dust particles and appears to form a shape, volume scattering in Cycles can be thought of as light reflecting off of many tiny dust particles. The possibilities of the volume scatter shader include anything from sunbeams (a.k.a. god rays), to thick clouds of smoke.

ColorSimply controls what color or light will be reflected by the volume. The input can be an RGB or any texture.

DensityDetermines how thick the volume appears to be. You can think of this as adding more “dust” to a dusty room. If you want to vary the density of your volume in different areas, use a map for the density. A map could be a 3D (procedural) texture or the factor from a smoke or fire simulation.

AnisotropyAnisotropy is the scattering direction depending on which way the light ray is moving. Positive values let the ray scatter in the direction it is traveling, while negative values cause the ray to scatter opposite of its travel direction. So in an evenly lit scene it does not make that much of a difference. However it is important to understand anisotropy as it can be tricky without first seeing its effects, so let’s take a look at some examples:

Fig. 2.18) Volume scatter with anisotropy. For positive values (left), rays mostly get scattered along the direction of the ray that entered the volume. Negative values mostly scatter into the opposite direction (right). Anisotropy of 0.0 (center) will result in random scatter directions. Depending on the density, rays might not get scattered at all.

Fig. 2.18) Renderings with a volume scatter material. From left to right the density was increased, the values were: 1, 10, 25, 50, 500. Top down the anisotropy was set to -1, -0.5, 0, 0.5 and 1. Notice that a volume scatter material with a high density looks fairly similar to the diffuse shader. The color of the shader is the same powder blue I use for all of the test renderings, the appearing color however is its complementary color, since blue got scattered away. The grey parts are where the scattered powder blue mixes with its complementary color, which is most visible for high densities.

Fig. 2.19) Volume scatter material with no color but 80% grey instead. Since there is no color, there is no complementary color, either (compare this to fig. 2.18).

Fig. 2.20) Renderings with a volume scatter material. From left to right the anisotropy was increased. The values are -0.9, -0.5