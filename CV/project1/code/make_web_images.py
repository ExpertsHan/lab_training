"""make_web_images.py：產生網頁用的縮圖與示意圖，存到 web/images/。

用法（在 project1/ 底下執行，需先跑過 main.py）：
    python code/make_web_images.py
"""
from pathlib import Path

import numpy as np
import skimage.io as skio
from skimage import img_as_float, img_as_ubyte
from skimage.transform import rescale

from align import load_plate, split_bgr, stack_rgb, downsample

MAX_W = 1000
OUT = Path("out")
WEB = Path("web/images")


def save(path, img, max_w=MAX_W):
    img = np.clip(img_as_float(img), 0, 1)
    if img.shape[1] > max_w:
        img = rescale(img, max_w / img.shape[1], channel_axis=2 if img.ndim == 3 else None,
                      anti_aliasing=True)
    skio.imsave(path, img_as_ubyte(np.clip(img, 0, 1)))


def zoom(img, y0, y1, x0, x1):
    """以比例 (0~1) 取出局部。"""
    h, w = img.shape[:2]
    return img[int(h * y0):int(h * y1), int(w * x0):int(w * x1)]


def main():
    WEB.mkdir(parents=True, exist_ok=True)

    # 1. 所有結果縮圖
    for f in sorted(OUT.glob("*.jpg")):
        save(WEB / f.name, skio.imread(f))

    # 2. 原始底片與未對齊的 baseline
    plate = load_plate("data/cathedral.jpg")
    save(WEB / "cathedral_plate.jpg", plate, max_w=400)
    b, g, r = split_bgr(plate)
    save(WEB / "cathedral_baseline.jpg", stack_rgb(r, g, b))

    # 3. emir 局部放大：RGB NCC vs. gradient NCC
    for tag in ["ncc_rgb_refb", "ncc_grad_refb"]:
        im = skio.imread(OUT / f"emir_pyramid_{tag}.jpg")
        save(WEB / f"emir_zoom_{tag}.jpg", zoom(im, 0.15, 0.45, 0.3, 0.7), max_w=700)

    # 4. Anti-aliasing：直接取樣 vs. 2x2 平均（harvesters G 通道縮小 8 倍後的局部）
    ch = split_bgr(load_plate("data/harvesters.tif"))[1]
    naive, box = ch, ch
    for _ in range(3):
        naive = naive[::2, ::2]
        box = downsample(box)
    for name, x in [("naive", naive), ("box", box)]:
        crop = zoom(x, 0.55, 0.85, 0.15, 0.65)
        up = np.kron(crop, np.ones((2, 2)))   # 最近鄰放大，方便看清楚像素
        save(WEB / f"aliasing_{name}.jpg", up, max_w=700)

    print("網頁圖片已存到", WEB)


if __name__ == "__main__":
    main()
