"""main.py：批次對齊 data/ 下所有影像，印出位移與耗時，並存成 JPG。

用法（在 project1/ 底下執行）：
    python code/main.py                      # 全部影像，RGB NCC，以 B 為基準
    python code/main.py --metric l2
    python code/main.py --feature grad       # 梯度特徵（Bells & Whistles）
    python code/main.py --only emir church   # 只跑部分檔案
"""
import argparse
import csv
import time
from pathlib import Path

import numpy as np
import skimage.io as skio
from skimage import img_as_ubyte

from align import (load_plate, colorize, identity, gradient_magnitude)

# ---- 固定參數：所有影像共用同一組 ----
CROP = 0.1           # 計分時四周各裁 10%
MIN_SIZE = 150       # 金字塔最粗層短邊下限（TIF 會縮 16 倍到 ~200 px）
COARSE_WINDOW = 15   # 最粗層搜尋 ±15
FINE_WINDOW = 3      # 其餘各層微調 ±3
SINGLE_WINDOW = 15   # 單尺度搜尋 ±15


def save_jpg(path, rgb):
    skio.imsave(path, img_as_ubyte(np.clip(rgb, 0, 1)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="out")
    p.add_argument("--metric", choices=["ncc", "l2"], default="ncc")
    p.add_argument("--feature", choices=["rgb", "grad"], default="rgb")
    p.add_argument("--ref", choices=["b", "g"], default="b")
    p.add_argument("--only", nargs="*", help="只處理這些檔名（不含副檔名）")
    args = p.parse_args()

    feature_fn = gradient_magnitude if args.feature == "grad" else identity
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.metric}_{args.feature}_ref{args.ref}"

    paths = sorted(Path(args.data).glob("*.jpg")) + sorted(Path(args.data).glob("*.tif"))
    if args.only:
        paths = [q for q in paths if q.stem in args.only]

    rows = []
    print(f"{'image':<24}| {'method':<8}| {'G (dx, dy)':<12}| {'R (dx, dy)':<12}| {'B (dx, dy)':<12}| time (s)")
    print("-" * 90)
    for path in paths:
        im = load_plate(path)
        # JPG 兩種方法都跑；TIF 只跑金字塔（單尺度太慢）
        methods = ["single", "pyramid"] if path.suffix == ".jpg" else ["pyramid"]
        for method in methods:
            kw = dict(metric=args.metric, crop=CROP)
            if method == "single":
                kw.update(window=SINGLE_WINDOW)
            else:
                kw.update(min_size=MIN_SIZE, coarse_window=COARSE_WINDOW,
                          fine_window=FINE_WINDOW, feature_fn=feature_fn)
            t0 = time.perf_counter()
            rgb, shifts = colorize(im, method=method, ref=args.ref, **kw)
            dt = time.perf_counter() - t0

            save_jpg(out_dir / f"{path.stem}_{method}_{tag}.jpg", rgb)
            fmt = lambda c: str(shifts.get(c, (0, 0)))
            print(f"{path.name:<24}| {method:<8}| {fmt('g'):<12}| {fmt('r'):<12}| {fmt('b'):<12}| {dt:6.2f}")
            rows.append([path.name, method, tag, *shifts.get("g", (0, 0)),
                         *shifts.get("r", (0, 0)), *shifts.get("b", (0, 0)), round(dt, 2)])

    with open(out_dir / f"offsets_{tag}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["image", "method", "tag", "g_dx", "g_dy", "r_dx", "r_dy", "b_dx", "b_dy", "time_s"])
        w.writerows(rows)
    print(f"\n結果存在 {out_dir}/，位移表：{out_dir}/offsets_{tag}.csv")


if __name__ == "__main__":
    main()

