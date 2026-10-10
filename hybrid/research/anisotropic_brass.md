# source: https://blenderartists.org/t/anisotropic-brass/1453500

# Anisotropic Brass - Materials and Textures - Blender Artists Community
URL: https://blenderartists.org/t/anisotropic-brass/1453500
Published: 2023-03-06

Anisotropic Brass - Materials and Textures - Blender Artists Community

# Anisotropic Brass 

 Duthomhas (Michael Thomas Greer) March 6, 2023, 11:53am 1 

I am trying to create an Anisotropic Brass (for both Eevee and Cycles). This is what I’ve managed so far:

The problem is in that bright orange-yellow tone showing up in the mid range in Cycles. (You can see it in Eevee too, but barely). In Cycles it can grow to dominate the image if the angle is just right.

This is my node setup (sorry for the big pic):

I’ve been struggling to learn materials for a while now, and I’m not sure I have any real idea what I’m doing. The basis for this material started from El Brujo De La Tribu’s metal materials pack brass for cycles…

I have tried to find the source of this bright orange by simply disconnecting things, but nothing seems to affect it. At this point I don’t know what I am doing wrong. (I created this material, just to be clear.)

 CarlG (CarlG) March 6, 2023, 12:04pm 2 

Do you have a reference image? I doubt those scratches are oriented that consistently in the real thing, and that the axels are also brass. I would also focus on Cycles, since only that can do anisotropic semi good. Eevee is just about faking it and probably no node resources could be shared like you’re attempting to do. Anisotropic materials isn’t just a “grab them off a library and slap them on” deal; different radial tangents possibly mixed with UV tangents, different brushing directions, satin polished or brushed scratchmarks, how to best utilize UV space and so on.

 Duthomhas (Michael Thomas Greer) March 6, 2023, 1:21pm 3 

Here’s a usable reference: https://www.vandaking.com/media/images/MASKED/2605A-WM-LRG.jpg

Here’s another: https://cdn.shopify.com/s/files/1/0088/6885/5870/products/yamaha-piano-wheel-2_1024x1024@2x.jpg?v=1671923708 I do notice that this ref has that bright orange too, lol. Staring at the real thing the light I have does not bring that out.

There’s nothing wrong with brass axels. You tend to get them on higher-end pianos because they’re prettier.

Orientation and randomness of scratches can be changed — I’m still messing with it — but yes, most of the time it will follow the curve of the wheel instead of cutting across like I have it.

I am not sure what you mean by your last bit about “slapping on” anisotropy. I’m just trying to make things look believably pretty, and I would just like a pointer or two in the right direction without having to become a materials scientist. I didn’t think my question was about the anisotropy in my images… As far as I know that’s not the issue (and it is currently not very easy to see in the cycles — remove the scratches and it’s there).

 Duthomhas (Michael Thomas Greer) March 6, 2023, 2:03pm 4 

Here’s another view to show the issue I am concerned about:

Notice how it is very bright under the music shelf. There shouldn’t be enough light getting in there to make it so bright and orange.

Likewise you can see the lower ed