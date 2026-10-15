import numpy as np
from skimage import img_as_float

img=np.zeros((4,6))
img[1,4]=1.0
print("shape (H, W) = ",img.shape)
print(img)

rgb=np.zeros((2,2,3))
rgb[0,0]=[1,0,0]
print("rgb shape=",rgb.shape)

a=np.array([200],dtype=np.uint8)
b=np.array([250], dtype=np.uint8)
print("uint 200-250=", a-b)
print("float 200-250=", a.astype(float)-b)

u8=np.array([0,128,250],dtype=np.uint8)
u16=np.array([0,32768,65535],dtype=np.uint16)
print("uint8",img_as_float(u8))
print("uint16", img_as_float(u16))
