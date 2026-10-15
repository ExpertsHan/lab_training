import sys

import numpy as np
import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_float

path=sys.argv[1] if len(sys.argv)>1 else "/Users/zhanjiahan/Documents/lab_training/CV/project1/data/cathedral.jpg"

im=skio.imread(path)
print("原始：",im.dtype,im.shape,"min/max=",im.min(),im.max())
im=img_as_float(im)
print("float:",im.dtype,"min/max=",im.min(),im.max())

h=im.shape[0]//3
b=im[0*h:1*h]
g=im[1*h:2*h]
r=im[2*h:3*h]
assert b.shape==g.shape==r.shape
print("shape=",b.shape)

fig, axes =plt.subplots(1,3,figsize=(12,5))
for ax,ch,name in zip(axes,[b,g,r],["B","G","R"]):
	ax.imshow(ch,cmap="gray", vmin=0,vmax=1)
	ax.set_title(f"{name} mean={ch.mean():.3f}")
	ax.axis("off")
plt.tight_layout()
plt.savefig("/Users/zhanjiahan/Documents/lab_training/CV/project1/out/s03_channels.jpg", dpi=100)
plt.show()

