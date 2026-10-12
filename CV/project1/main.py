import numpy as np
import skimage.io as skio
from skimage import img_as_float

im=skio.imread("data/cathedral.jpg")
print(im.dtype,im.shape)
im=img_as_float(im)
