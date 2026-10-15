"""關卡二：不對齊直接疊起來。執行：python code/s04_baseline.py data/cathedral.jpg"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_float, img_as_ubyte

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/zhanjiahan/documents/lab_training/CV/project1/data/cathedral.jpg")

im = img_as_float(skio.imread(path))
h = im.shape[0] // 3
b, g, r = im[:h], im[h:2 * h], im[2 * h:3 * h]

color = np.dstack([r, g, b])        # 注意：R, G, B 順序！
color = np.clip(color, 0, 1)

out = Path("out") / f"{path.stem}_baseline.jpg"
skio.imsave(out, img_as_ubyte(color))
print("已存:", out)

plt.figure(figsize=(6, 6))
plt.imshow(color)
plt.title("No alignment (color fringing)")
plt.axis("off")
plt.show()

