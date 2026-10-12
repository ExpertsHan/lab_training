# CS180 Project 1 解題導引：Prokudin-Gorskii 影像彩色化

> 作業原文：<https://cal-cs180.github.io/fa26/hw/proj1/index.html>
> 繳交方式：<https://cal-cs180.github.io/fa26/hw/submitting.html>
>
> 這份文件的目標是：
> 1. 把整個 project 拆成可以一步一步驗證的小關卡（每關都有 ✅ 檢查點）
> 2. 每一關先講「你需要懂的觀念」，再講「要做什麼」，最後給「提示」
> 3. 提示分層放在可折疊的 `<details>` 裡——**卡住再打開**，先自己想
> 4. 每一節最後都有「📦 本節完整範例程式碼」（同樣折疊起來），內容都已在實際資料上跑過驗證
>
> 正文中的核心邏輯仍以虛擬碼與數學式描述；建議先照著正文自己實作，再展開範例對照。範例程式的檔案結構：
>
> | 檔案 | 內容 | 出現在 |
> |---|---|---|
> | `code/align.py` | 讀圖、切割、L2/NCC、平移、單尺度、金字塔、`colorize` | 關卡一～六逐步累加 |
> | `code/enhance.py` | 自動裁切、對比、白平衡、色彩映射 | 關卡十 |
> | `code/main.py` | 批次處理所有影像、計時、輸出 JPG 與位移 CSV | 關卡七 |
> | `code/s0X_*.py`、`debug_tools.py`、`tests.py` … | 每一節的示範／檢查腳本 | 各節 |
>
> 所有指令都在 `project1/` 底下執行，例如 `python code/main.py`。

---

## 目錄

- [0. 全局地圖：你要做什麼、學到什麼](#0-全局地圖你要做什麼學到什麼)
- [1. 環境與專案結構](#1-環境與專案結構)
- [2. 背景知識：數位影像就是陣列](#2-背景知識數位影像就是陣列)
- [3. 關卡一：讀圖與切成三個通道](#3-關卡一讀圖與切成三個通道)
- [4. 關卡二：不對齊直接疊起來（建立 baseline）](#4-關卡二不對齊直接疊起來建立-baseline)
- [5. 關卡三：相似度指標 L2 與 NCC](#5-關卡三相似度指標-l2-與-ncc)
- [6. 關卡四：平移影像與邊界問題](#6-關卡四平移影像與邊界問題)
- [7. 關卡五：單尺度窮舉搜尋（Single-scale）](#7-關卡五單尺度窮舉搜尋single-scale)
- [8. 關卡六：影像金字塔（Multi-scale Pyramid）](#8-關卡六影像金字塔multi-scale-pyramid)
- [9. 關卡七：批次處理全部影像、計時、輸出](#9-關卡七批次處理全部影像計時輸出)
- [10. 關卡八：除錯與失敗分析](#10-關卡八除錯與失敗分析)
- [11. 關卡九：自己挑 3 張以上 LoC 影像](#11-關卡九自己挑-3-張以上-loc-影像)
- [12. 關卡十：Bells & Whistles](#12-關卡十bells--whistles)
- [13. 關卡十一：網頁報告與繳交](#13-關卡十一網頁報告與繳交)
- [14. 最終檢查清單](#14-最終檢查清單)
- [15. 自我測驗](#15-自我測驗)
- [16. 延伸閱讀](#16-延伸閱讀)

---

## 0. 全局地圖：你要做什麼、學到什麼

### 0.1 任務一句話

一張玻璃底片掃描檔裡，由上到下有三張黑白照片，分別是透過 **B、G、R** 濾鏡拍的同一個場景（注意順序是 **BGR**，不是 RGB）。你要把它切成三份、**找出 G 和 R 相對於 B 的 (x, y) 位移**，對齊之後疊成一張彩色照片。

```
┌──────────────┐
│   Blue 濾鏡   │  ← 第 1 份（當作基準 / reference）
├──────────────┤
│  Green 濾鏡   │  ← 第 2 份，要對齊到 B
├──────────────┤
│   Red 濾鏡    │  ← 第 3 份，要對齊到 B
└──────────────┘
```

### 0.2 你最後要交的東西

| 項目 | 內容 |
|---|---|
| 程式碼 | `code/main.py`（或 `.ipynb`）＋ `README.txt`，上傳 Gradescope（**不要**放圖片） |
| 網頁 | 一個公開網頁（建議 GitHub Pages），印成 `web/page.pdf` 一起放進 zip |
| Google Form | 把網頁 URL 交到課程 gallery 表單 |

### 0.3 評分重點（CS180）

- **Single-scale（60%）**：`cathedral`、`monastery`、`tobolsk` 三張 JPG 對齊無瑕疵 ＋ 網頁上有完整說明
- **Multi-scale pyramid（40%）**：17 張（14 張官方 + 3 張自選）中最多 1 張失敗 ＋ 網頁上把 NCC / L2、金字塔每一步講清楚
- **注意**：即使你用了更好的方法（例如 gradient 特徵），網頁上**仍必須**展示用基本 L2 / NCC（在 RGB 像素上）的結果，否則報告分數會被扣
- CS280A 學生：Bells & Whistles 中的 5 項是**必做**（自動裁切、自動對比、自動白平衡、更好的色彩映射、更好的特徵）

### 0.4 學習地圖

| 關卡 | 你會學到的觀念 |
|---|---|
| 1 | 影像在記憶體中的表示、`dtype`（uint8 / uint16 / float）、正規化 |
| 2 | 色彩通道、RGB 合成、色差（color fringing）的成因 |
| 3 | 影像相似度量測：L2 距離、Normalized Cross-Correlation 以及它的不變性 |
| 4 | 影像平移、座標系慣例、邊界效應（boundary effect） |
| 5 | 窮舉搜尋（brute-force search）、時間複雜度、向量化 |
| 6 | 影像金字塔、取樣定理與 aliasing、高斯模糊、coarse-to-fine 策略、遞迴 |
| 7 | 效能量測、輸出格式、型別轉換與 clipping |
| 8 | 視覺化除錯技巧、為什麼「亮度不一致」會讓像素比較失效 |
| 10 | 邊緣/梯度特徵、直方圖與對比、色彩恆常性與白平衡、色彩空間的線性轉換 |
| 11 | 技術寫作：把實驗結果講成一個故事 |

---

## 1. 環境與專案結構

### 1.1 建議環境

```bash
cd ~/Documents/lab_training/CV/project1
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scikit-image matplotlib
```

- `numpy`：所有運算核心
- `scikit-image`（`skimage`）：讀寫圖片、型別轉換、（可選）resize / filter
- `matplotlib`：在 notebook 或視窗中顯示圖片

> 💡 如果你偏好 notebook，可以再 `pip install jupyter`。開發用 notebook 很方便看圖，但**最終要能用一個 `main.py` 或 `main.ipynb` 重現所有結果**。

### 1.2 下載資料

作業頁面的 `data.zip`（Google Drive 連結）。解壓到 `data/`。裡面會有：

- 3 張小 JPG：`cathedral.jpg`、`monastery.jpg`、`tobolsk.jpg`（約 400 × 1000 px 量級）
- 約 11 張大 TIF：例如 `emir.tif`、`church.tif`、`harvesters.tif`、`icon.tif`、`melons.tif`、`self_portrait.tif` …（每張約 3000 × 9000 px 量級，十幾 MB 到上百 MB）

先用 `ls -lh data/` 看一下檔案大小，你會立刻理解為什麼後面需要金字塔。

### 1.3 建議專案結構

```
project1/
├── data/               # 原始資料（不要上傳到 Gradescope）
├── out/                # 輸出結果（.jpg）
├── code/
│   ├── main.py         # 進入點：跑全部圖片、印出位移、存檔
│   ├── align.py        # 對齊相關：metric、shift、single-scale、pyramid
│   ├── enhance.py      # （可選）bells & whistles：crop、contrast、WB…
│   └── README.txt
└── web/
    └── index.html      # 網頁（也可以獨立成另一個 GitHub repo）
```

> 📌 作業最後提醒：「你在 Project 2 會再用到 image pyramid——寫乾淨、可重用的程式」。所以把金字塔寫成**獨立、通用的函式**，不要和這次的對齊邏輯綁死。

### 1.4 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

執行 `python code/s01_check_env.py`：印出套件版本、列出 `data/` 內所有影像與大小，並建立 `out/`、`web/images/`。之後所有腳本都假設你在 `project1/` 底下執行。

<details>
<summary>🖥️ 建立環境（bash）</summary>

```bash
cd ~/Documents/lab_training/CV/project1
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy scikit-image matplotlib
mkdir -p code out web/images
```
</details>

<details>
<summary>📄 <code>code/s01_check_env.py</code></summary>

```python
"""關卡 1：確認環境與資料。執行：python code/s01_check_env.py"""
import sys
from pathlib import Path

import numpy as np
import skimage
import matplotlib

print("Python     :", sys.version.split()[0])
print("numpy      :", np.__version__)
print("scikit-image:", skimage.__version__)
print("matplotlib :", matplotlib.__version__)

data = Path("data")
assert data.is_dir(), "找不到 data/，請確認是在 project1/ 底下執行，且已解壓 data.zip"

files = sorted(data.glob("*.jpg")) + sorted(data.glob("*.tif"))
print(f"\n共 {len(files)} 張影像：")
for f in files:
    print(f"  {f.name:<24} {f.stat().st_size / 1e6:8.1f} MB")

for d in ["out", "web/images"]:
    Path(d).mkdir(parents=True, exist_ok=True)
print("\n已建立 out/ 與 web/images/")
```
</details>

---

## 2. 背景知識：數位影像就是陣列

### 2.1 灰階影像 = 2D 陣列

一張灰階影像在 numpy 中是 shape 為 `(H, W)` 的陣列。`img[r, c]` 是第 `r` 列（row，往下）、第 `c` 行（column，往右）的像素亮度。

- **row 索引 ↔ y 方向（垂直）**
- **column 索引 ↔ x 方向（水平）**

這一點後面會反覆用到：作業要你印出 `(x, y)` 位移，而 numpy 的 `axis=0` 是 y、`axis=1` 是 x。**很多人在這裡搞反。**

### 2.2 彩色影像 = 3D 陣列

shape 為 `(H, W, 3)`，最後一維依序是 R、G、B（對 `skimage` / `matplotlib` 而言）。

### 2.3 dtype 與數值範圍

| 格式 | 常見 dtype | 範圍 |
|---|---|---|
| JPG | `uint8` | 0 ~ 255 |
| TIF（本作業） | `uint16` | 0 ~ 65535 |
| 運算用 | `float64` / `float32` | 一般正規化到 0.0 ~ 1.0 |

**為什麼一定要轉成 float？**

1. **溢位（overflow）**：`uint8` 的 `200 - 250` 不會是 `-50`，而是 `206`（wrap around）。你算 L2 時會得到完全錯誤的數字。
2. **一致性**：JPG 和 TIF 範圍不同，轉成 `[0, 1]` 的 float 之後，同一套參數（例如門檻值）就能套用到兩種格式。

`skimage.img_as_float(img)` 會根據原始 dtype 自動除以正確的最大值。

> 🧠 **學到的知識**：影像處理中最常見的 bug 之一就是型別問題。養成習慣：**讀進來立刻轉 float，存檔前才轉回整數型別**。

### 2.4 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

執行 `python code/s02_arrays.py`，親眼看到座標慣例、`uint8` 溢位，以及 `img_as_float` 對不同 dtype 的處理。

<details>
<summary>📄 <code>code/s02_arrays.py</code></summary>

```python
"""關卡 2 背景知識：陣列、座標、dtype。執行：python code/s02_arrays.py"""
import numpy as np
from skimage import img_as_float

# 2.1 灰階影像 = 2D 陣列：img[row, col] = img[y, x]
img = np.zeros((4, 6))          # H=4（y 方向）, W=6（x 方向）
img[1, 4] = 1.0                 # y=1, x=4
print("shape (H, W) =", img.shape)
print(img)

# 2.2 彩色影像 = 3D 陣列 (H, W, 3)，最後一維是 R, G, B
rgb = np.zeros((2, 2, 3))
rgb[0, 0] = [1, 0, 0]           # 左上角是紅色
print("rgb shape =", rgb.shape)

# 2.3 uint8 溢位
a = np.array([200], dtype=np.uint8)
b = np.array([250], dtype=np.uint8)
print("uint8 200 - 250 =", a - b)                      # [206]，不是 -50
print("float 200 - 250 =", a.astype(float) - b)        # [-50.]

# img_as_float 會依 dtype 除以正確的最大值
u8 = np.array([0, 128, 255], dtype=np.uint8)
u16 = np.array([0, 32768, 65535], dtype=np.uint16)
print("uint8  ->", img_as_float(u8))
print("uint16 ->", img_as_float(u16))
```
</details>

---

## 3. 關卡一：讀圖與切成三個通道

### 3.1 要做的事

1. 讀入一張圖片（先用 `cathedral.jpg`）
2. 轉成 float
3. 把高度三等分，切出 `b`、`g`、`r` 三張灰階圖

### 3.2 需要的 API（這部分只是 API 用法，直接給）

```python
import numpy as np
import skimage.io as skio
from skimage import img_as_float

im = skio.imread("data/cathedral.jpg")
print(im.dtype, im.shape)          # 先觀察！
im = img_as_float(im)
```

### 3.3 你要思考的問題

- `im.shape[0]` 不一定能被 3 整除。該怎麼處理？
- 切出來的三張圖 shape 必須**完全相同**，否則後面不能逐像素比較。

<details>
<summary>💡 提示 1：怎麼算每份的高度</summary>

用整數除法 `//` 取每份的高度 `h`，然後第 k 份就是 `im[k*h : (k+1)*h]`。多出來的 1～2 列直接丟掉即可（它們都在底片的邊框上，不重要）。
</details>

### 3.4 ✅ 檢查點

用 matplotlib 並排顯示三張灰階圖（`plt.imshow(x, cmap="gray")`）。你應該看到：

- 三張圖內容幾乎一樣，但**亮度分布不同**（例如藍天在 B 通道很亮、在 R 通道比較暗）
- 每張圖都有黑白相間、不規則的邊框

> 🧠 **學到的知識**：同一個場景在不同波長濾鏡下的「亮度」不同——這正是後面 `emir.tif` 會失敗的根本原因。現在先記住這個觀察。

### 3.5 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

兩份程式：**獨立腳本**讓你直接跑看結果；**`align.py` 的開頭**把同樣的邏輯整理成可重用的函式（後面每一關都會往 `align.py` 裡加函式）。

<details>
<summary>📄 <code>code/s03_split.py</code>（獨立腳本）</summary>

```python
"""關卡一：讀圖並切成 B、G、R。執行：python code/s03_split.py data/cathedral.jpg"""
import sys

import numpy as np
import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_float

path = sys.argv[1] if len(sys.argv) > 1 else "data/cathedral.jpg"

im = skio.imread(path)
print("原始:", im.dtype, im.shape, "min/max =", im.min(), im.max())
im = img_as_float(im)
print("float:", im.dtype, "min/max =", im.min(), im.max())

h = im.shape[0] // 3                # 每份高度；多出來的 1~2 列丟掉
b = im[0 * h:1 * h]
g = im[1 * h:2 * h]
r = im[2 * h:3 * h]
assert b.shape == g.shape == r.shape
print("每個通道 shape:", b.shape)

fig, axes = plt.subplots(1, 3, figsize=(12, 5))
for ax, ch, name in zip(axes, [b, g, r], ["B", "G", "R"]):
    ax.imshow(ch, cmap="gray", vmin=0, vmax=1)
    ax.set_title(f"{name}  mean={ch.mean():.3f}")
    ax.axis("off")
plt.tight_layout()
plt.savefig("out/s03_channels.jpg", dpi=100)
plt.show()
```
</details>

<details>
<summary>📄 <code>code/align.py</code>（開頭 + 關卡一的函式）</summary>

```python
"""align.py：Prokudin-Gorskii 三通道對齊的核心函式。"""
import numpy as np
import skimage.io as skio
from skimage import img_as_float
from scipy.ndimage import gaussian_filter, sobel


# ---------- 關卡一：讀圖與切割 ----------
def load_plate(path):
    """讀入玻璃底片掃描檔，回傳 float32、值域 [0, 1] 的灰階陣列。"""
    im = skio.imread(path)
    if im.ndim == 3:                      # 少數檔案可能被存成多通道，取第一個
        im = im[..., 0]
    return img_as_float(im).astype(np.float32)


def split_bgr(im):
    """把高度三等分，依序回傳 (b, g, r)。多出來的 1~2 列直接丟掉。"""
    h = im.shape[0] // 3
    b = im[0 * h:1 * h]
    g = im[1 * h:2 * h]
    r = im[2 * h:3 * h]
    return b, g, r
```
</details>

---

## 4. 關卡二：不對齊直接疊起來（建立 baseline）

### 4.1 要做的事

不做任何對齊，直接把三張圖疊成彩色圖並顯示。

### 4.2 你要知道的

- `np.dstack([r, g, b])` 會產生 `(H, W, 3)`。**順序是 R、G、B**——不要把底片上「由上到下」的 B、G、R 順序直接塞進去。
- 顯示 float 影像時，matplotlib 期待值在 `[0, 1]`。

### 4.3 ✅ 檢查點

你會看到一張有明顯「彩色鬼影」的圖：物體邊緣有紅、綠、藍錯開的輪廓。這叫 **color fringing**，成因就是三個通道沒對齊。

**把這張圖存起來**——它會是你網頁上「Before」的好素材。

> 🧠 **學到的知識**：在報告中，**一個好的 baseline 讓你的方法更有說服力**。之後每加一個改進，都和前一版比較。

### 4.4 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

執行 `python code/s04_baseline.py data/cathedral.jpg`，會存出 `out/cathedral_baseline.jpg`（網頁上的 Before 圖）。

<details>
<summary>📄 <code>code/s04_baseline.py</code>（獨立腳本）</summary>

```python
"""關卡二：不對齊直接疊起來。執行：python code/s04_baseline.py data/cathedral.jpg"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_float, img_as_ubyte

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/cathedral.jpg")

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
```
</details>

<details>
<summary>📄 加進 <code>code/align.py</code> 的函式</summary>

```python
# ---------- 關卡二：疊成彩色 ----------
def stack_rgb(r, g, b):
    """注意順序是 R, G, B。"""
    return np.clip(np.dstack([r, g, b]), 0, 1)
```
</details>

---

## 5. 關卡三：相似度指標 L2 與 NCC

這是整個 project 的理論核心。對齊問題可以寫成一個最佳化問題：

$$
(d_x^*, d_y^*) = \arg\min_{(d_x, d_y) \in \text{window}} \; \text{cost}\big(\text{shift}(I, d_x, d_y),\; \text{ref}\big)
$$

你需要一個 `cost`（或 `score`）函式來衡量兩張圖「有多像」。

### 5.1 L2 距離（Euclidean distance / SSD）

$$
\text{L2}(A, B) = \sqrt{\sum_{i,j} \big(A_{ij} - B_{ij}\big)^2}
$$

- 越**小**越好
- 實務上可以不開根號（Sum of Squared Differences, SSD），因為開根號是單調函數，不改變 argmin，還能省計算
- **弱點**：如果 B 整體比 A 亮 0.2，就算完全對齊，L2 也很大。它假設兩張圖「亮度值本身」相同。

### 5.2 NCC（Normalized Cross-Correlation）

步驟：

1. 把影像攤平成向量 $\mathbf{a}$、$\mathbf{b}$
2. 減去平均值：$\tilde{\mathbf{a}} = \mathbf{a} - \bar{a}$
3. 除以 L2 norm：$\hat{\mathbf{a}} = \tilde{\mathbf{a}} / \|\tilde{\mathbf{a}}\|$
4. 取內積：

$$
\text{NCC}(A, B) = \hat{\mathbf{a}} \cdot \hat{\mathbf{b}} = \frac{\sum (a_i - \bar a)(b_i - \bar b)}{\sqrt{\sum (a_i - \bar a)^2}\,\sqrt{\sum (b_i - \bar b)^2}}
$$

- 範圍 $[-1, 1]$，越**大**越好（1 代表完全線性正相關）
- 它其實就是兩個向量的 **cosine similarity**（在去平均之後）——也就是統計上的 **Pearson 相關係數**

### 5.3 為什麼 NCC 通常比 L2 好？——不變性（invariance）

若 $B = \alpha A + \beta$（$\alpha > 0$），也就是 B 是 A 的「亮度平移 + 對比縮放」：

- 減平均 → 消掉 $\beta$（亮度偏移）
- 除以 norm → 消掉 $\alpha$（對比縮放）

所以 $\text{NCC}(A, B) = 1$。**NCC 對仿射亮度變化不變**，而 L2 沒有這個性質。

> ⚠️ 但 NCC 只能處理**線性**的亮度關係。如果某個區域在 B 很亮、在 R 很暗，而另一個區域相反（例如 emir 的藍色衣服），那就不是 $\alpha A + \beta$ 能描述的了——NCC 也會失效。這是 Bells & Whistles「Better features」的動機。

### 5.4 要做的事

寫兩個函式：

```python
def l2_score(a, b):
    """回傳 a 與 b 的 L2 距離（或 SSD），越小越好。a, b 為相同 shape 的 float 陣列。"""
    # TODO

def ncc_score(a, b):
    """回傳 a 與 b 的 NCC，越大越好。"""
    # TODO
```

建議讓兩者的「好壞方向」一致，例如讓搜尋函式統一取 **最大值**，那就讓 L2 回傳負值；或者讓搜尋函式接受一個參數說明要取 min 還是 max。自己決定，但要一致。

### 5.5 實作要點

- **全部用 numpy 向量運算**（`np.sum`、`np.mean`、`np.linalg.norm`），不要用 Python 迴圈跑每個像素。差距可以是 100 倍以上。
- 要不要攤平（`ravel`）都可以——`np.sum` 對多維陣列也是全部加總。
- 防呆：如果 norm 是 0（整張圖是常數）會除以零。實務上幾乎不會發生，但可以加一個很小的 `eps`。

### 5.6 ✅ 單元測試（自己寫、自己跑）

| 測試 | 預期 |
|---|---|
| `ncc_score(a, a)` | ≈ 1.0 |
| `ncc_score(a, 2*a + 0.3)` | ≈ 1.0（驗證不變性） |
| `ncc_score(a, -a)` | ≈ -1.0 |
| `l2_score(a, a)` | 0 |
| `l2_score(a, a + 0.3)` | 很大（驗證 L2 **沒有**不變性） |

> 🧠 **學到的知識**：選擇相似度指標＝選擇你假設兩張圖之間是什麼關係。L2 假設「值相同」，NCC 假設「值線性相關」，之後的 gradient / edge 特徵則假設「結構（邊緣位置）相同」。這個思考框架在整個電腦視覺領域都通用（例如 stereo matching、template matching、影像配準）。

### 5.7 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

這裡採用「兩個 metric 都是**越大越好**」的設計：L2 回傳負的 SSD，搜尋函式一律取最大值。執行 `python code/s05_metrics.py` 會跑完 5.6 的所有單元測試。

<details>
<summary>📄 <code>code/s05_metrics.py</code>（含單元測試）</summary>

```python
"""關卡三：L2 / NCC 與單元測試。執行：python code/s05_metrics.py"""
import numpy as np


def l2_score(a, b):
    """負的 SSD：越大（越接近 0）越好。統一成「越大越好」方便搜尋函式取 max。"""
    d = a - b
    return -float(np.sum(d * d))


def ncc_score(a, b, eps=1e-8):
    """Normalized Cross-Correlation，範圍 [-1, 1]，越大越好。"""
    a = a - a.mean()
    b = b - b.mean()
    return float(np.sum(a * b) / (np.linalg.norm(a) * np.linalg.norm(b) + eps))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    a = rng.random((100, 120))

    assert np.isclose(ncc_score(a, a), 1.0)
    assert np.isclose(ncc_score(a, 2 * a + 0.3), 1.0)   # 仿射亮度不變性
    assert np.isclose(ncc_score(a, -a), -1.0)
    assert l2_score(a, a) == 0.0
    print("l2(a, a + 0.3) =", l2_score(a, a + 0.3))      # 很負 → L2 沒有不變性
    print("ncc(a, random) =", ncc_score(a, rng.random(a.shape)))  # 接近 0
    print("全部測試通過 ✅")
```
</details>

<details>
<summary>📄 加進 <code>code/align.py</code> 的函式</summary>

```python
# ---------- 關卡三：相似度指標（統一成「越大越好」） ----------
def l2_score(a, b):
    """負的 SSD：越大（越接近 0）越好。"""
    d = a - b
    return -float(np.sum(d * d))


def ncc_score(a, b, eps=1e-8):
    """Normalized Cross-Correlation，範圍 [-1, 1]，越大越好。"""
    a = a - a.mean()
    b = b - b.mean()
    return float(np.sum(a * b) / (np.linalg.norm(a) * np.linalg.norm(b) + eps))


METRICS = {"l2": l2_score, "ncc": ncc_score}
```
</details>

---

## 6. 關卡四：平移影像與邊界問題

### 6.1 平移

作業建議用 `np.roll`：

```python
np.roll(img, shift=(dy, dx), axis=(0, 1))
```

- `axis=0` 是 row → 對應 **y**
- `axis=1` 是 column → 對應 **x**
- 正的 `dx` 代表往右移、正的 `dy` 代表往下移

### 6.2 `np.roll` 的副作用：環繞（wrap-around）

`np.roll` 會把從右邊推出去的像素塞回左邊。所以平移後的影像邊緣有一條「錯誤的」像素帶。

### 6.3 更嚴重的問題：底片本身的邊框

觀察關卡一的圖：每張都有黑色/白色的邊框，而且三個通道的邊框**位置並不一致**、還有刮痕和雜訊。如果你在整張圖上算 L2/NCC，**這些邊框的強烈對比會主導分數**，演算法會努力「對齊邊框」而不是對齊內容。

### 6.4 解法：只在內部區域算分數

作業 Final Advice 也明說：*Ignore borders when scoring; compute metrics on interior pixels.*

做法：算分數前，把兩張圖的四周各裁掉一個比例（例如每邊 10%～20%），只比較中間。

<details>
<summary>💡 提示 1：裁切要用比例還是固定像素？</summary>

用**比例**。因為同一套程式要跑 JPG（小）和 TIF（大），而且在金字塔的不同層級上影像大小也不同。用比例可以讓「同一組參數」在所有尺度都合理。
</details>

<details>
<summary>💡 提示 2：裁切的時機</summary>

平移之後、算分之前裁切。這樣 `np.roll` 環繞進來的那條錯誤像素也會一起被裁掉——只要你的裁切寬度大於搜尋範圍。想想看為什麼？
</details>

### 6.5 要做的事

寫一個小工具函式，例如：

```python
def crop_interior(img, frac):
    """回傳四周各裁掉 frac 比例後的中間區域。"""
    # TODO
```

### 6.6 ✅ 檢查點

- 對一張圖 `np.roll` 之後，用 `plt.imshow` 確認它往你**預期的方向**移動
- 確認 `crop_interior` 輸出的 shape 正確

> 🧠 **學到的知識**：**邊界效應（boundary effect）**在影像處理中無所不在——卷積、平移、濾波都會遇到。常見的處理方式有：裁掉、補零（zero padding）、鏡射（reflect padding）、環繞（wrap）。在這個問題中，最簡單也最有效的是「不看邊界」。

### 6.7 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

執行 `python code/s06_shift.py`：驗證平移方向、裁切後的 shape，並畫出 `np.roll` 的 wrap-around 與裁切後的樣子。

<details>
<summary>📄 <code>code/s06_shift.py</code></summary>

```python
"""關卡四：平移與內部裁切。執行：python code/s06_shift.py"""
import numpy as np
import matplotlib.pyplot as plt


def shift(img, dx, dy):
    """正 dx 往右、正 dy 往下。axis=0 是 y（row），axis=1 是 x（column）。"""
    return np.roll(img, shift=(dy, dx), axis=(0, 1))


def crop_interior(img, frac):
    """四周各裁掉 frac 比例，只留中間。"""
    h, w = img.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    return img[ch:h - ch, cw:w - cw]


if __name__ == "__main__":
    img = np.zeros((10, 10))
    img[2, 3] = 1                                   # 亮點在 (x=3, y=2)
    moved = shift(img, dx=4, dy=1)
    y, x = np.argwhere(moved == 1)[0]
    print(f"平移後亮點在 (x={x}, y={y})")             # 預期 (7, 3)
    assert (x, y) == (7, 3)

    big = np.ones((400, 300))
    print("crop_interior shape:", crop_interior(big, 0.1).shape)   # (320, 240)
    assert crop_interior(big, 0.1).shape == (320, 240)

    # 看 wrap-around：把一張漸層往右推 30 px，最左邊會出現原本最右邊的亮像素
    grad = np.tile(np.linspace(0, 1, 200), (100, 1))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3))
    axes[0].imshow(grad, cmap="gray"); axes[0].set_title("original")
    axes[1].imshow(shift(grad, 30, 0), cmap="gray"); axes[1].set_title("roll dx=30 (wrap-around)")
    axes[2].imshow(crop_interior(shift(grad, 30, 0), 0.2), cmap="gray"); axes[2].set_title("crop 20%")
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.show()
    print("全部測試通過 ✅")
```
</details>

<details>
<summary>📄 加進 <code>code/align.py</code> 的函式</summary>

```python
# ---------- 關卡四：平移與裁切 ----------
def shift(img, dx, dy):
    """正 dx 往右、正 dy 往下。axis=0 是 y（row），axis=1 是 x（column）。"""
    return np.roll(img, shift=(dy, dx), axis=(0, 1))


def crop_interior(img, frac):
    """四周各裁掉 frac 比例，只留中間。"""
    h, w = img.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    return img[ch:h - ch, cw:w - cw]
```
</details>

---

## 7. 關卡五：單尺度窮舉搜尋（Single-scale）

### 7.1 演算法

```
function align_single(moving, ref, window, metric):
    best_score ← 最差值
    best_shift ← (0, 0)
    for dx in [-window, ..., +window]:
        for dy in [-window, ..., +window]:
            shifted ← shift(moving, dx, dy)
            score ← metric(crop_interior(shifted), crop_interior(ref))
            if score 比 best_score 好:
                更新 best_score, best_shift
    return best_shift
```

外層兩個迴圈是 OK 的（只有 31×31 ≈ 961 次），但 `metric` 內部一定要向量化。

### 7.2 介面建議

```python
def align_single_scale(moving, ref, window=15, metric="ncc", crop=0.1):
    """
    在 [-window, window]^2 內窮舉 (dx, dy)，回傳讓 moving 最像 ref 的位移。
    回傳值：(dx, dy)，dx 為水平位移（column）、dy 為垂直位移（row）。
    """
    # TODO
```

讓 `window` 和 `metric` 可以調整，因為等一下金字塔會**重用這個函式**。

### 7.3 主流程

```
b, g, r ← split(image)
(gx, gy) ← align(g, b)
(rx, ry) ← align(r, b)
g_aligned ← shift(g, gx, gy)
r_aligned ← shift(r, rx, ry)
color ← stack(r_aligned, g_aligned, b)
print("G:", (gx, gy), "R:", (rx, ry))
```

### 7.4 ✅ 檢查點

在三張 JPG 上跑，用 NCC 和 L2 各跑一次。你可以拿以下**大約值**對照方向和量級（以 B 為基準，格式 `(dx, dy)`，不同裁切比例可能差 ±1 px）：

| 圖片 | G 大約位移 | R 大約位移 |
|---|---|---|
| cathedral | (2, 5) | (3, 12) |
| monastery | (2, -3) | (2, 3) |
| tobolsk | (3, 3) | (3, 6) |

- 如果你的數字 x、y 對調了 → 回去看關卡四的座標慣例
- 如果數字的正負號全部相反 → 你可能是在算「ref 要怎麼移才會對齊 moving」，或 `np.roll` 方向理解反了
- 如果數字很奇怪（例如貼著 ±15 的邊界）→ 很可能是邊框在主導分數，加大裁切比例

**用眼睛看結果最重要**：放大看物體邊緣，不應該有彩色鬼影。

### 7.5 思考題：時間複雜度

設影像有 $N$ 個像素、搜尋範圍是 $[-W, W]$，單尺度搜尋的成本是：

$$
O\big((2W+1)^2 \cdot N\big)
$$

- JPG：$N \approx 400 \times 340$，$W=15$ → 約 $1.3 \times 10^8$ 次運算，幾秒內完成
- TIF：$N \approx 3200 \times 3700$，而位移可能到 **150 px 以上**，若 $W=200$ → 約 $1.9 \times 10^{12}$ 次運算 → **好幾個小時**

這就是下一關的動機。

> 🧠 **學到的知識**：窮舉搜尋保證找到搜尋範圍內的全域最佳解，但成本隨搜尋範圍**平方**成長、隨影像大小**線性**成長。兩者都很大時就必須換策略。

### 7.6 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

`align_single_scale` 多了一個 `center` 參數（預設 `(0, 0)`）：在 `center` 附近搜尋。單尺度時用不到，但下一關的金字塔會靠它「在粗層答案附近微調」。`return_scores=True` 會回傳分數地圖，關卡八除錯會用到。

實測結果（RGB NCC 與 L2 都一樣）：cathedral G (2, 5) R (3, 12)；monastery G (2, −3) R (2, 3)；tobolsk G (3, 3) R (3, 6)，每張約 0.3 秒。

<details>
<summary>📄 加進 <code>code/align.py</code> 的函式</summary>

```python
# ---------- 關卡五：單尺度窮舉搜尋 ----------
def align_single_scale(moving, ref, window=15, metric="ncc", crop=0.1,
                       center=(0, 0), return_scores=False):
    """
    在 center 附近 [-window, window]^2 內窮舉 (dx, dy)，回傳讓 moving 最像 ref 的位移 (dx, dy)。
    return_scores=True 時額外回傳 (2W+1, 2W+1) 的分數地圖（row 對應 dy、col 對應 dx）。
    """
    score_fn = METRICS[metric]
    ref_c = crop_interior(ref, crop)
    cx, cy = center
    best_score, best = -np.inf, (cx, cy)
    scores = np.empty((2 * window + 1, 2 * window + 1))
    for i, dy in enumerate(range(cy - window, cy + window + 1)):
        for j, dx in enumerate(range(cx - window, cx + window + 1)):
            s = score_fn(crop_interior(shift(moving, dx, dy), crop), ref_c)
            scores[i, j] = s
            if s > best_score:
                best_score, best = s, (dx, dy)
    return (best, scores) if return_scores else best
```
</details>

<details>
<summary>📄 <code>code/s07_single_scale.py</code>（跑三張 JPG、兩種 metric）</summary>

```python
"""關卡五：單尺度窮舉搜尋。執行：python code/s07_single_scale.py
（函式本體同 align.py 的 align_single_scale；這裡用 import 重用關卡一～四的函式）"""
import time
from pathlib import Path

import skimage.io as skio
from skimage import img_as_ubyte

from align import load_plate, split_bgr, shift, stack_rgb, align_single_scale

for name in ["cathedral", "monastery", "tobolsk"]:
    im = load_plate(f"data/{name}.jpg")
    b, g, r = split_bgr(im)
    for metric in ["ncc", "l2"]:
        t0 = time.perf_counter()
        gx, gy = align_single_scale(g, b, window=15, metric=metric, crop=0.1)
        rx, ry = align_single_scale(r, b, window=15, metric=metric, crop=0.1)
        dt = time.perf_counter() - t0
        color = stack_rgb(shift(r, rx, ry), shift(g, gx, gy), b)
        out = Path("out") / f"{name}_single_{metric}.jpg"
        skio.imsave(out, img_as_ubyte(color))
        print(f"{name:<10} {metric:<4} G: ({gx}, {gy})  R: ({rx}, {ry})  {dt:.2f}s  -> {out}")
```
</details>

---

## 8. 關卡六：影像金字塔（Multi-scale Pyramid）

### 8.1 核心直覺

> 在縮小 2 倍的圖上，原本 100 px 的位移變成 50 px；縮小 32 倍時只剩約 3 px。

所以：

1. 在**最小的圖**上用小視窗窮舉，找到粗略位移
2. 回到大一倍的圖，把位移 ×2 當作初始猜測，只在附近（例如 ±2 px）微調
3. 一路回到原圖

這就是 **coarse-to-fine** 策略。

```
Level 3 (1/8)   ■          ← 在這裡大範圍搜尋（便宜，因為圖很小）
Level 2 (1/4)   ■■         ← 位移 ×2，小範圍微調
Level 1 (1/2)   ■■■■       ← 位移 ×2，小範圍微調
Level 0 (原圖)  ■■■■■■■■   ← 位移 ×2，小範圍微調（在大圖上只看少數位置）
```

### 8.2 先學一個重要觀念：降採樣與 aliasing

最直覺的縮小方法是 `img[::2, ::2]`（每隔一個像素取一個）。但這樣會出問題：

- **取樣定理（Nyquist）**：要正確表示一個訊號，取樣頻率至少要是訊號最高頻率的 2 倍。
- 直接丟掉一半像素，等於取樣頻率減半；原圖中的高頻細節（細紋、雜訊、刮痕）會「折疊」成假的低頻圖樣，叫做 **aliasing**（你在拍螢幕、條紋衣服時看到的摩爾紋就是它）。
- aliasing 會讓小圖出現原圖中不存在的結構，可能誤導粗層級的對齊。

**正確做法：先低通濾波（模糊），再降採樣。**

常見的低通濾波：

| 方法 | 說明 |
|---|---|
| 2×2 區塊平均 | 最簡單：每 2×2 個像素取平均成 1 個。本身就是一種 box filter + 降採樣 |
| 高斯模糊後取樣 | 標準做法。高斯 kernel 的頻率響應平滑、沒有 ringing。$\sigma \approx 1$ 對 2 倍降採樣很常用 |
| `skimage.transform.rescale(..., anti_aliasing=True)` | 作業允許使用 resize 類函式；它內部會先做高斯模糊 |

> 📌 作業規定：**可以**用 resize 這類基本函式，但**不能**用現成的「Gaussian/Laplacian pyramid」高階函式或「自動對齊」函式（例如 `skimage.transform.pyramid_gaussian`、`skimage.registration.phase_cross_correlation`、OpenCV 的 `findTransformECC` 等）。金字塔的建構與 coarse-to-fine 邏輯要自己寫。
>
> 如果你想挑戰自己，可以只用 numpy 實作「高斯 kernel + 卷積 + 取樣」；這在 Project 2 會很有用。

<details>
<summary>💡 提示：2×2 區塊平均用 numpy 怎麼寫（不給完整答案）</summary>

先把影像裁成偶數寬高，然後思考：`img[0::2, 0::2]`、`img[1::2, 0::2]`、`img[0::2, 1::2]`、`img[1::2, 1::2]` 這四個陣列分別是什麼？把它們平均起來會得到什麼？

另一個思路：`reshape` 成 `(H/2, 2, W/2, 2)` 之後對某兩個 axis 取平均。
</details>

### 8.3 寫一個通用的降採樣函式

```python
def downsample(img):
    """先低通濾波再 2 倍降採樣，回傳寬高約為一半的影像。"""
    # TODO
```

（可選）再寫一個建構整座金字塔的函式，回傳一個 list：`[原圖, 1/2, 1/4, ...]`。這個函式在 Project 2 可以直接重用。

### 8.4 金字塔對齊：遞迴版思路

```
function align_pyramid(moving, ref):
    if 影像夠小（例如短邊 < 某個門檻）:
        return align_single(moving, ref, window = 大視窗)     # base case

    # 1. 遞迴：在縮小一半的圖上先求解
    (dx, dy) ← align_pyramid(downsample(moving), downsample(ref))

    # 2. 把粗層級的答案放大回目前尺度
    (dx, dy) ← (2·dx, 2·dy)

    # 3. 在這個初始猜測附近做小範圍微調
    moving_shifted ← shift(moving, dx, dy)
    (ddx, ddy) ← align_single(moving_shifted, ref, window = 小視窗)

    return (dx + ddx, dy + ddy)
```

作業原文說：「It is very easy to implement by adding recursive calls to your original single-scale implementation.」——就是這個意思。

你也可以寫成**迭代版**：先建好整座金字塔的 list，然後從最小那層往回迴圈。兩者等價，選你覺得清楚的。

### 8.5 要你自己決定的參數（並在網頁上說明理由）

| 參數 | 思考方向 |
|---|---|
| 最粗層級的大小（遞迴停止條件） | 太大 → 最粗層搜尋慢；太小 → 圖上幾乎沒有資訊、容易找錯。常見選擇：短邊約 100～400 px |
| 最粗層的搜尋視窗 | 必須涵蓋「原圖最大位移 ÷ 2^層數」。TIF 中 R 的位移可能到 ~150～180 px，若縮小 32 倍約剩 5～6 px，±15 綽綽有餘 |
| 每層微調的視窗 | 粗層的誤差放大 2 倍後頂多 ±1～2 px，所以 ±2 ～ ±4 通常足夠。越小越快 |
| 裁切比例 | 和單尺度一致即可（用比例，所以每層自動適用） |

> ⚠️ **一致性**：作業要求「使用一組固定參數，不要針對每張圖調參」。

### 8.6 效能優化提示

- **最花時間的是最細那層**（原圖上），因為 $N$ 最大。在原圖上的微調視窗盡量小。
- 在原圖上計算分數時，可以考慮只算中心區域（裁切比例本來就在減少計算量）。
- 使用 `float32` 而不是 `float64` 可以加速、省記憶體（可選，精度上對本作業足夠）。
- 目標：**每張 TIF 1 分鐘以內**。如果你跑超過幾分鐘，先用 `time.perf_counter()` 量每一層花多久，找出瓶頸。

<details>
<summary>💡 提示：TIF 跑很久的常見原因</summary>

1. 在原圖上用了大視窗（例如每層都用 ±15）
2. metric 函式裡有 Python 迴圈
3. 每次迴圈都重新做 `img_as_float` 或重新建金字塔
4. 在原圖上反覆 `np.roll` 整張大圖——可以思考是否能先裁出中心區域再平移（注意要留足夠的邊界給平移量）
</details>

### 8.7 ✅ 檢查點

1. 先在 JPG 上跑金字塔版，結果應該和單尺度**相同或只差 1 px**
2. 再跑一張 TIF（建議先用 `church.tif` 或 `harvesters.tif`），確認：
   - 幾十秒內完成
   - 結果無明顯鬼影
   - G 的位移通常是數十 px，R 的位移可能到一百多 px（大約是 G 的兩倍——想想為什麼？提示：三張圖是依序曝光的，相機或底片在拍攝間持續移動）

> 🧠 **學到的知識**：
> - **影像金字塔**是電腦視覺最基本的多尺度表示，之後會出現在 blending（Project 2）、optical flow（Lucas-Kanade 金字塔版）、特徵偵測（SIFT 的 scale space）、深度學習（FPN）等。
> - **Coarse-to-fine** 把搜尋成本從 $O(W^2 N)$ 降到大約 $O(\log W \cdot N)$ 量級，是一種「用近似換速度」的經典策略。
> - **代價**：如果粗層級找錯了（例如被大片相似紋理誤導），細層級的小視窗**無法修正**。這是金字塔方法的固有風險。

### 8.8 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

這段包含：`downsample`（2×2 區塊平均或高斯模糊再取樣）、`build_pyramid`、**迭代版** `align_pyramid`、**遞迴版** `align_pyramid_recursive`（兩者答案相同），以及把整個流程包起來的 `colorize`。`feature_fn`、`gradient_magnitude` 是為 12.5 準備的，基本版用預設的 `identity` 即可。

> ⚠️ **參數的陷阱（實測踩到的）**：金字塔能找到的最大位移約為 $W_\text{coarse}\cdot 2^L + W_\text{fine}\cdot(2^L - 1)$，$L$ 是降採樣次數。若最粗層停在短邊 ≥ 300 px，TIF 只會縮 8 倍（$L=3$），最大可達約 $15\cdot 8 + 3\cdot 7 = 141$ px——而 `melons`、`self_portrait` 的 R 位移約 **176～178 px**，結果會被卡在 141 而對不齊。所以這裡用 `min_size=150`（縮 16 倍到約 200 px，$L=4$，最大可達約 285 px）。

實測（Apple Silicon）：`church.tif` 每層估計為 (0,4) → (−1,7) → (−1,15) → (−2,29) → (−4,58)，兩個通道合計約 3.4 秒。

<details>
<summary>📄 加進 <code>code/align.py</code> 的函式</summary>

```python
# ---------- 關卡六：影像金字塔 ----------
def downsample(img, method="box", sigma=1.0):
    """先低通濾波再 2 倍降採樣。method: "box"（2x2 平均）或 "gaussian"。"""
    if method == "gaussian":
        return gaussian_filter(img, sigma=sigma)[::2, ::2]
    h, w = img.shape[0] // 2 * 2, img.shape[1] // 2 * 2
    img = img[:h, :w]
    return img.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))


def build_pyramid(img, min_size=150, method="box"):
    """回傳 [原圖, 1/2, 1/4, ...]，直到短邊 < 2*min_size 為止（最後一層短邊 >= min_size）。"""
    pyr = [img]
    while min(pyr[-1].shape[:2]) >= 2 * min_size:
        pyr.append(downsample(pyr[-1], method=method))
    return pyr


def identity(x):
    return x


def gradient_magnitude(img):
    """Sobel 梯度大小，作為「更好的特徵」。"""
    gx = sobel(img, axis=1)
    gy = sobel(img, axis=0)
    return np.hypot(gx, gy)


def align_pyramid(moving, ref, metric="ncc", crop=0.1, min_size=150,
                  coarse_window=15, fine_window=3, feature_fn=identity,
                  verbose=False):
    """
    迭代版 coarse-to-fine 對齊，回傳原圖尺度下的 (dx, dy)。
    feature_fn 會在每一層把影像轉成特徵圖（例如 gradient_magnitude）後再比較。
    """
    pm = build_pyramid(moving, min_size)
    pr = build_pyramid(ref, min_size)
    dx, dy = 0, 0
    for level in range(len(pm) - 1, -1, -1):          # 從最小那層往回
        m, r = feature_fn(pm[level]), feature_fn(pr[level])
        window = coarse_window if level == len(pm) - 1 else fine_window
        dx, dy = align_single_scale(m, r, window=window, metric=metric,
                                    crop=crop, center=(dx, dy))
        if verbose:
            print(f"  level {level} {m.shape}: ({dx}, {dy})")
        if level > 0:
            dx, dy = 2 * dx, 2 * dy                   # 放大回下一層的尺度
    return dx, dy


def align_pyramid_recursive(moving, ref, metric="ncc", crop=0.1, min_size=150,
                            coarse_window=15, fine_window=3):
    """遞迴版，與 align_pyramid 等價（feature_fn 省略）。"""
    if min(moving.shape) < 2 * min_size:              # base case
        return align_single_scale(moving, ref, coarse_window, metric, crop)
    dx, dy = align_pyramid_recursive(downsample(moving), downsample(ref),
                                     metric, crop, min_size, coarse_window, fine_window)
    return align_single_scale(moving, ref, fine_window, metric, crop,
                              center=(2 * dx, 2 * dy))


# ---------- 整合：一張底片 → 彩色圖 ----------
def colorize(im, method="pyramid", ref="b", **kw):
    """
    回傳 (color, shifts)。shifts 是 dict，例如 {"g": (dx, dy), "r": (dx, dy)}。
    ref="b" 為作業預設；ref="g" 則把 B、R 對齊到 G。
    """
    b, g, r = split_bgr(im)
    chans = {"b": b, "g": g, "r": r}
    align_fn = align_pyramid if method == "pyramid" else align_single_scale
    shifts = {}
    for name in "bgr":
        if name == ref:
            continue
        shifts[name] = align_fn(chans[name], chans[ref], **kw)
        chans[name] = shift(chans[name], *shifts[name])
    return stack_rgb(chans["r"], chans["g"], chans["b"]), shifts
```
</details>

<details>
<summary>📄 <code>code/s08_pyramid.py</code>（印出每一層的估計、驗證遞迴版 = 迭代版）</summary>

```python
"""關卡六：金字塔對齊。執行：python code/s08_pyramid.py data/church.tif"""
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_ubyte

from align import (load_plate, split_bgr, shift, stack_rgb, build_pyramid,
                   align_single_scale, align_pyramid, align_pyramid_recursive)

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/church.tif")
im = load_plate(path)
b, g, r = split_bgr(im)

# 1. 看一下金字塔每層的大小
pyr = build_pyramid(b, min_size=150)
print("金字塔各層:", [p.shape for p in pyr])

# 2. 迭代版（印出每一層的估計）
t0 = time.perf_counter()
print("G -> B"); gx, gy = align_pyramid(g, b, verbose=True)
print("R -> B"); rx, ry = align_pyramid(r, b, verbose=True)
dt = time.perf_counter() - t0
print(f"{path.name}: G ({gx}, {gy})  R ({rx}, {ry})  {dt:.2f}s")

# 3. 遞迴版應該得到相同答案
assert align_pyramid_recursive(g, b) == (gx, gy)
assert align_pyramid_recursive(r, b) == (rx, ry)

# 4. JPG 上：金字塔 vs 單尺度
if path.suffix == ".jpg":
    print("single-scale G:", align_single_scale(g, b), " R:", align_single_scale(r, b))

color = stack_rgb(shift(r, rx, ry), shift(g, gx, gy), b)
out = Path("out") / f"{path.stem}_pyramid.jpg"
skio.imsave(out, img_as_ubyte(color))
print("已存:", out)

fig, axes = plt.subplots(1, len(pyr), figsize=(3 * len(pyr), 3))
for i, (ax, p) in enumerate(zip(axes, pyr)):
    ax.imshow(p, cmap="gray"); ax.set_title(f"level {i}: {p.shape}"); ax.axis("off")
plt.tight_layout()
plt.show()
```
</details>

<details>
<summary>📄 完整的 <code>code/align.py</code>（關卡一～六合併後）</summary>

```python
"""align.py：Prokudin-Gorskii 三通道對齊的核心函式。"""
import numpy as np
import skimage.io as skio
from skimage import img_as_float
from scipy.ndimage import gaussian_filter, sobel


# ---------- 關卡一：讀圖與切割 ----------
def load_plate(path):
    """讀入玻璃底片掃描檔，回傳 float32、值域 [0, 1] 的灰階陣列。"""
    im = skio.imread(path)
    if im.ndim == 3:                      # 少數檔案可能被存成多通道，取第一個
        im = im[..., 0]
    return img_as_float(im).astype(np.float32)


def split_bgr(im):
    """把高度三等分，依序回傳 (b, g, r)。多出來的 1~2 列直接丟掉。"""
    h = im.shape[0] // 3
    b = im[0 * h:1 * h]
    g = im[1 * h:2 * h]
    r = im[2 * h:3 * h]
    return b, g, r


# ---------- 關卡二：疊成彩色 ----------
def stack_rgb(r, g, b):
    """注意順序是 R, G, B。"""
    return np.clip(np.dstack([r, g, b]), 0, 1)


# ---------- 關卡三：相似度指標（統一成「越大越好」） ----------
def l2_score(a, b):
    """負的 SSD：越大（越接近 0）越好。"""
    d = a - b
    return -float(np.sum(d * d))


def ncc_score(a, b, eps=1e-8):
    """Normalized Cross-Correlation，範圍 [-1, 1]，越大越好。"""
    a = a - a.mean()
    b = b - b.mean()
    return float(np.sum(a * b) / (np.linalg.norm(a) * np.linalg.norm(b) + eps))


METRICS = {"l2": l2_score, "ncc": ncc_score}


# ---------- 關卡四：平移與裁切 ----------
def shift(img, dx, dy):
    """正 dx 往右、正 dy 往下。axis=0 是 y（row），axis=1 是 x（column）。"""
    return np.roll(img, shift=(dy, dx), axis=(0, 1))


def crop_interior(img, frac):
    """四周各裁掉 frac 比例，只留中間。"""
    h, w = img.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    return img[ch:h - ch, cw:w - cw]


# ---------- 關卡五：單尺度窮舉搜尋 ----------
def align_single_scale(moving, ref, window=15, metric="ncc", crop=0.1,
                       center=(0, 0), return_scores=False):
    """
    在 center 附近 [-window, window]^2 內窮舉 (dx, dy)，回傳讓 moving 最像 ref 的位移 (dx, dy)。
    return_scores=True 時額外回傳 (2W+1, 2W+1) 的分數地圖（row 對應 dy、col 對應 dx）。
    """
    score_fn = METRICS[metric]
    ref_c = crop_interior(ref, crop)
    cx, cy = center
    best_score, best = -np.inf, (cx, cy)
    scores = np.empty((2 * window + 1, 2 * window + 1))
    for i, dy in enumerate(range(cy - window, cy + window + 1)):
        for j, dx in enumerate(range(cx - window, cx + window + 1)):
            s = score_fn(crop_interior(shift(moving, dx, dy), crop), ref_c)
            scores[i, j] = s
            if s > best_score:
                best_score, best = s, (dx, dy)
    return (best, scores) if return_scores else best


# ---------- 關卡六：影像金字塔 ----------
def downsample(img, method="box", sigma=1.0):
    """先低通濾波再 2 倍降採樣。method: "box"（2x2 平均）或 "gaussian"。"""
    if method == "gaussian":
        return gaussian_filter(img, sigma=sigma)[::2, ::2]
    h, w = img.shape[0] // 2 * 2, img.shape[1] // 2 * 2
    img = img[:h, :w]
    return img.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))


def build_pyramid(img, min_size=150, method="box"):
    """回傳 [原圖, 1/2, 1/4, ...]，直到短邊 < 2*min_size 為止（最後一層短邊 >= min_size）。"""
    pyr = [img]
    while min(pyr[-1].shape[:2]) >= 2 * min_size:
        pyr.append(downsample(pyr[-1], method=method))
    return pyr


def identity(x):
    return x


def gradient_magnitude(img):
    """Sobel 梯度大小，作為「更好的特徵」。"""
    gx = sobel(img, axis=1)
    gy = sobel(img, axis=0)
    return np.hypot(gx, gy)


def align_pyramid(moving, ref, metric="ncc", crop=0.1, min_size=150,
                  coarse_window=15, fine_window=3, feature_fn=identity,
                  verbose=False):
    """
    迭代版 coarse-to-fine 對齊，回傳原圖尺度下的 (dx, dy)。
    feature_fn 會在每一層把影像轉成特徵圖（例如 gradient_magnitude）後再比較。
    """
    pm = build_pyramid(moving, min_size)
    pr = build_pyramid(ref, min_size)
    dx, dy = 0, 0
    for level in range(len(pm) - 1, -1, -1):          # 從最小那層往回
        m, r = feature_fn(pm[level]), feature_fn(pr[level])
        window = coarse_window if level == len(pm) - 1 else fine_window
        dx, dy = align_single_scale(m, r, window=window, metric=metric,
                                    crop=crop, center=(dx, dy))
        if verbose:
            print(f"  level {level} {m.shape}: ({dx}, {dy})")
        if level > 0:
            dx, dy = 2 * dx, 2 * dy                   # 放大回下一層的尺度
    return dx, dy


def align_pyramid_recursive(moving, ref, metric="ncc", crop=0.1, min_size=150,
                            coarse_window=15, fine_window=3):
    """遞迴版，與 align_pyramid 等價（feature_fn 省略）。"""
    if min(moving.shape) < 2 * min_size:              # base case
        return align_single_scale(moving, ref, coarse_window, metric, crop)
    dx, dy = align_pyramid_recursive(downsample(moving), downsample(ref),
                                     metric, crop, min_size, coarse_window, fine_window)
    return align_single_scale(moving, ref, fine_window, metric, crop,
                              center=(2 * dx, 2 * dy))


# ---------- 整合：一張底片 → 彩色圖 ----------
def colorize(im, method="pyramid", ref="b", **kw):
    """
    回傳 (color, shifts)。shifts 是 dict，例如 {"g": (dx, dy), "r": (dx, dy)}。
    ref="b" 為作業預設；ref="g" 則把 B、R 對齊到 G。
    """
    b, g, r = split_bgr(im)
    chans = {"b": b, "g": g, "r": r}
    align_fn = align_pyramid if method == "pyramid" else align_single_scale
    shifts = {}
    for name in "bgr":
        if name == ref:
            continue
        shifts[name] = align_fn(chans[name], chans[ref], **kw)
        chans[name] = shift(chans[name], *shifts[name])
    return stack_rgb(chans["r"], chans["g"], chans["b"]), shifts
```
</details>

---

## 9. 關卡七：批次處理全部影像、計時、輸出

### 9.1 要做的事

在 `main.py` 中：

1. 走訪 `data/` 下所有 `.jpg` 與 `.tif`
2. 對每張圖：讀取 → 切割 → 對齊（G→B、R→B）→ 疊合 → 存檔
3. 印出（並記錄成表格）：檔名、G 位移、R 位移、耗時
4. 輸出存成 **JPG**（作業建議，節省空間）

### 9.2 存檔注意事項

- float 影像存成 JPG 前要轉回 `uint8`：可用 `skimage.img_as_ubyte`，但它要求值在 `[0, 1]`——先用 `np.clip(img, 0, 1)` 保險
- 對 JPG 輸入，單尺度和金字塔版本建議都輸出，網頁上兩者都要展示

### 9.3 建議輸出的資訊表

```
image               | G (dx, dy) | R (dx, dy) | time (s)
--------------------|------------|------------|---------
cathedral.jpg       |  ( ?,  ?)  |  ( ?,  ?)  |   ?
...
```

這張表直接放上網頁就是「List the offsets you computed」的 deliverable。

### 9.4 讓程式可重現

- 用 `argparse` 或檔案頂端常數管理參數（metric、裁切比例、視窗大小）
- `README.txt` 寫清楚：需要哪些套件、資料放哪裡、怎麼執行、輸出在哪裡

> 🧠 **學到的知識**：研究/工程中，「可重現」和「正確」一樣重要。助教要能用你的 `main.py` 重新產生所有結果。

### 9.5 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

`main.py` 把前面所有東西串起來：同一組固定參數、JPG 跑單尺度 + 金字塔、TIF 只跑金字塔、印出表格並輸出 CSV。所有圖都用 `colorize()`，所以切換 metric / 特徵 / 基準通道只要改命令列參數。

實測輸出（RGB NCC、以 B 為基準，每張 TIF 約 3.5 秒）：

```
image                   | method  | G (dx, dy)  | R (dx, dy)  | time (s)
cathedral.jpg           | single  | (2, 5)      | (3, 12)     |   0.29
monastery.jpg           | single  | (2, -3)     | (2, 3)      |   0.31
tobolsk.jpg             | single  | (3, 3)      | (3, 6)      |   0.34
church.tif              | pyramid | (4, 25)     | (-4, 58)    |   3.22
emir.tif                | pyramid | (24, 49)    | (-205, 141) |   3.40   ← 失敗（見關卡八）
harvesters.tif          | pyramid | (17, 60)    | (13, 124)   |   3.28
icon.tif                | pyramid | (17, 41)    | (23, 89)    |   3.34
ilemselga.tif           | pyramid | (7, 40)     | (11, 130)   |   3.43
melons.tif              | pyramid | (10, 82)    | (13, 178)   |   3.42
religous_painting.tif   | pyramid | (3, 28)     | (7, 68)     |   3.36
self_portrait.tif       | pyramid | (29, 79)    | (37, 176)   |   3.48
siren.tif               | pyramid | (-6, 49)    | (-25, 96)   |   3.46
three_generations.tif   | pyramid | (14, 53)    | (11, 112)   |   3.33
wharf.tif               | pyramid | (-7, 15)    | (-16, 83)   |   3.41
```

<details>
<summary>📄 <code>code/main.py</code></summary>

```python
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
```
</details>

<details>
<summary>📄 <code>code/README.txt</code></summary>

```text
CS180 Project 1 - Prokudin-Gorskii Colorization

Requirements: Python 3.10+, numpy, scipy, scikit-image, matplotlib
    pip install numpy scipy scikit-image matplotlib

Layout (run everything from the project root, i.e. the folder containing data/):
    data/            input plates (.jpg / .tif)
    code/align.py    core: split, L2/NCC, shift, single-scale search, pyramid
    code/enhance.py  bells & whistles: auto crop, contrast, white balance, color mapping
    code/main.py     entry point

Run:
    python code/main.py                    # all images, RGB NCC, reference = B
    python code/main.py --metric l2        # L2 instead of NCC
    python code/main.py --feature grad     # gradient-magnitude features (fixes emir)
    python code/main.py --only emir        # a subset

Output:
    out/<name>_<method>_<metric>_<feature>_ref<b|g>.jpg
    out/offsets_<metric>_<feature>_ref<b|g>.csv   (G/R offsets as (dx, dy) and runtime)

Parameters (same for every image): crop 10% per side when scoring,
pyramid coarsest short side >= 150 px, coarse window +-15, fine window +-3.
```
</details>

---

## 10. 關卡八：除錯與失敗分析

### 10.1 視覺化除錯工具（強烈建議自己寫幾個小函式）

| 工具 | 做法 | 用途 |
|---|---|---|
| 放大局部 | 對齊後的結果裁一個 200×200 的區域放大顯示 | 細看邊緣有沒有色邊 |
| 差異圖 | 顯示 `|aligned_g - b|` | 對齊好的地方應該大部分接近黑色，只剩下「真正的內容差異」 |
| 棋盤格混合 | 把兩張圖用棋盤格交錯顯示 | 檢查格子邊界上的線條是否連續 |
| 分數地圖 | 把 (2W+1)×(2W+1) 每個位移的分數畫成熱圖 | 看最佳值是否是一個清楚的尖峰；若平坦或有多個峰，代表 metric 不可靠 |

### 10.2 常見 bug 清單

| 症狀 | 可能原因 |
|---|---|
| 全部圖片都偏一點點，方向一致 | x / y 搞反；或回傳了「反向」位移 |
| 位移總是貼著搜尋邊界（例如 ±15） | 邊框主導分數 → 增加裁切比例；或搜尋範圍不夠大 |
| 顏色怪怪的（例如天空是黃色） | `dstack` 順序錯（把 B 放在 R 的位置） |
| 結果整張很暗或全白 | 型別/範圍錯誤，例如 uint16 沒正規化 |
| 金字塔版和單尺度版差很多 | 位移沒 ×2；或遞迴回傳時忘了把粗層位移加回去；或降採樣產生 aliasing |
| TIF 跑超過 5 分鐘 | 見 8.6 |

### 10.3 預期的失敗案例：`emir.tif`

用 RGB 像素做 NCC/L2，`emir.tif`（布哈拉的埃米爾）的 **R 通道**通常會對不齊。

**原因（請在網頁上說明，這是 deliverable 的一部分）**：

- 埃米爾穿著鮮豔的藍色長袍：在 B 通道很亮、在 R 通道很暗
- 背景/其他區域可能剛好相反或不同
- 也就是說，B 和 R 之間的亮度關係**不是線性的**，甚至在不同區域符號相反 → NCC 假設的 $R \approx \alpha B + \beta$ 不成立

**常見的修正方向**（任選，這就是 Bells & Whistles 的範疇）：

1. **改用 G 當基準**：G 和 R、G 和 B 的關係通常都比 B 和 R 近（波長上 G 在中間）。把 B、R 都對齊到 G。
2. **改用邊緣/梯度特徵**：不比較亮度，比較「邊緣在哪裡」。不管衣服在哪個通道亮或暗，衣服的**輪廓**位置是一樣的。（詳見 12.5）

> 📌 作業允許 14 張官方圖中有 1 張失敗。但無論如何都要：**展示失敗的結果 + 解釋為什麼失敗**。如果你修好了，展示 before / after。

> 🧠 **學到的知識**：分析失敗比展示成功更能證明你懂。一個好的失敗分析要回答：「方法的哪個**假設**在這裡被打破了？」

### 10.4 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

`debug_tools.py` 實作了 10.1 表格中的四個工具（放大局部、差異圖、棋盤格、分數地圖），`__main__` 直接拿 `emir.tif` 示範：RGB NCC 把 R 對到 (−205, 141)，梯度 NCC 則得到 (40, 107)。比較兩張分數地圖，你會看到 RGB 版沒有清楚的單一尖峰。

<details>
<summary>📄 <code>code/debug_tools.py</code></summary>

```python
"""關卡八：視覺化除錯工具。執行：python code/debug_tools.py data/emir.tif"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from align import load_plate, split_bgr, shift, stack_rgb, align_pyramid, \
    align_single_scale, downsample, gradient_magnitude


def zoom(img, cy, cx, size=200):
    """以 (cx, cy) 為中心裁 size x size 的區域。"""
    h = size // 2
    return img[max(cy - h, 0):cy + h, max(cx - h, 0):cx + h]


def diff_image(a, b):
    """|a - b|：對齊好的地方應該大多接近黑色。"""
    return np.abs(a - b)


def checkerboard(a, b, tile=64):
    """兩張灰階圖棋盤格交錯，檢查格子邊界上的線條是否連續。"""
    yy, xx = np.indices(a.shape)
    mask = ((yy // tile) + (xx // tile)) % 2 == 0
    return np.where(mask, a, b)


def score_map(moving, ref, window=15, metric="ncc", crop=0.1):
    """回傳 (2W+1, 2W+1) 的分數地圖；row 對應 dy、col 對應 dx。"""
    _, scores = align_single_scale(moving, ref, window, metric, crop, return_scores=True)
    return scores


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/emir.tif")
    b, g, r = split_bgr(load_plate(path))
    rx, ry = align_pyramid(r, b)
    rx2, ry2 = align_pyramid(r, b, feature_fn=gradient_magnitude)
    print(f"R (RGB NCC): ({rx}, {ry})   R (gradient NCC): ({rx2}, {ry2})")

    r_al = shift(r, rx, ry)
    cy, cx = b.shape[0] // 2, b.shape[1] // 2

    # 在縮小 16 倍的圖上畫分數地圖（原圖畫會很慢）
    small = lambda x: downsample(downsample(downsample(downsample(x))))
    rs, bs = small(r), small(b)
    s_rgb = score_map(rs, bs)
    s_grad = score_map(gradient_magnitude(rs), gradient_magnitude(bs))

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes[0, 0].imshow(zoom(stack_rgb(r_al, shift(g, *align_pyramid(g, b)), b), cy, cx, 400))
    axes[0, 0].set_title("zoom (RGB NCC result)")
    axes[0, 1].imshow(diff_image(r_al, b), cmap="gray"); axes[0, 1].set_title("|R_aligned - B|")
    axes[0, 2].imshow(zoom(checkerboard(r_al, b), cy, cx, 600), cmap="gray")
    axes[0, 2].set_title("checkerboard R/B")
    for ax, s, t in [(axes[1, 0], s_rgb, "score map: RGB NCC (1/16)"),
                     (axes[1, 1], s_grad, "score map: gradient NCC (1/16)")]:
        im = ax.imshow(s, cmap="viridis", extent=[-15.5, 15.5, 15.5, -15.5])
        ax.set_xlabel("dx"); ax.set_ylabel("dy"); ax.set_title(t)
        fig.colorbar(im, ax=ax)
    axes[1, 2].imshow(zoom(checkerboard(shift(r, rx2, ry2), b), cy, cx, 600), cmap="gray")
    axes[1, 2].set_title("checkerboard R/B (gradient)")
    for ax in [axes[0, 0], axes[0, 1], axes[0, 2], axes[1, 2]]:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"out/{path.stem}_debug.jpg", dpi=80)
    plt.show()
```
</details>

---

## 11. 關卡九：自己挑 3 張以上 LoC 影像

### 11.1 去哪裡找

Library of Congress 的 Prokudin-Gorskii 典藏：<https://www.loc.gov/collections/prokudin-gorskii/?st=grid>

### 11.2 下載注意事項

- 你要的是**原始玻璃底片掃描**（垂直排列的三張黑白圖），**不是** LoC 已經合成好的彩色圖。進入單張作品頁面後，找到 negative / glass plate 的那個版本，下載 TIFF（通常是 `.tif`，檔名多以 `u` 結尾，例如 `xxxxxu.tif`）
- 檔案通常很大（幾十 MB），下載後先確認：是 3 張垂直排列、順序一樣是 B/G/R、dtype 為何
- 有些底片的三格大小或排列不規則，或有破損——挑之前先看一下

### 11.3 挑選建議

挑一些**有挑戰性但不至於崩壞**的：

- 有很多細節（建築、文字）→ 對齊好壞很明顯，視覺效果好
- 有強烈顏色的物體 → 可以拿來測試 emir 類型的問題
- 有移動物體（水、人、雲）→ 會有無法消除的色邊，可以拿來討論「平移模型的極限」

### 11.4 ✅ 檢查點

用**完全相同的參數**跑這些圖，把結果與位移加入網頁表格。

### 11.5 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

下載 LoC 底片後先執行 `python code/s11_inspect_loc.py data/xxxxxu.tif`，檢查 dtype、高寬比（三格垂直排列應約為 3），並預覽三個通道。確認沒問題後，把檔案放進 `data/`，再跑 `python code/main.py --only xxxxxu`，參數完全不用改。

<details>
<summary>📄 <code>code/s11_inspect_loc.py</code></summary>

```python
"""關卡九：檢查從 LoC 下載的底片。執行：python code/s11_inspect_loc.py data/xxxxxu.tif"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import skimage.io as skio

from align import load_plate, split_bgr

path = Path(sys.argv[1])
raw = skio.imread(path)
print(f"{path.name}: dtype={raw.dtype}, shape={raw.shape}, "
      f"size={path.stat().st_size / 1e6:.1f} MB")
if raw.ndim != 2:
    print("⚠️ 不是單通道灰階；load_plate 會只取第一個通道")
h, w = raw.shape[:2]
if not 2.4 < h / w < 3.6:
    print(f"⚠️ 高寬比 {h / w:.2f} 不像三格垂直排列（預期約 3），請確認下載的是 glass negative")

b, g, r = split_bgr(load_plate(path))
fig, axes = plt.subplots(1, 4, figsize=(14, 5), gridspec_kw={"width_ratios": [1, 1, 1, 1]})
axes[0].imshow(raw if raw.ndim == 2 else raw[..., 0], cmap="gray"); axes[0].set_title("plate")
for ax, ch, n in zip(axes[1:], [b, g, r], "BGR"):
    ax.imshow(ch, cmap="gray"); ax.set_title(n)
for ax in axes:
    ax.axis("off")
plt.tight_layout()
plt.show()
```
</details>

---

## 12. 關卡十：Bells & Whistles

> CS180：加分／炫技用；CS280A：前 5 項必做，每項 6 分（結果 20% + 說明 80%）。
> 每一項都要在網頁上提供：**動機、方法、before / after 對照**。
> 作業允許使用任何函式庫做 B&W，前提是你能解釋它在做什麼、為什麼用它。

### 12.1 自動裁切（Automatic cropping）

**目標**：自動偵測並移除黑邊、白邊、以及因三通道錯位造成的彩色邊。**不能**只是固定裁掉每邊 X%。

**需要的觀念**：

- 邊框的特徵：
  - 非常亮（白）或非常暗（黑）的連續列／行
  - 列／行之間有強烈的亮度跳變（邊框與內容的交界）
  - 對齊後，邊緣區域三個通道彼此**不一致**（作業的提示：好的區域通道間資訊一致，邊框則不然）

**可能的方法（由簡到難）**：

1. **列／行統計**：對每一列計算平均亮度（或標準差），從外往內掃描，找到第一個「看起來像內容」的位置（例如平均值落在某範圍、標準差夠大）
2. **邊緣偵測**：對靠近邊界的區域做水平/垂直方向的梯度，沿著每列/每行取平均，找梯度最強的那條線當作邊框交界
3. **通道一致性**：對齊後計算每列/每行上三通道的差異（例如 `|R-G| + |G-B|` 的平均），差異異常大的列/行屬於邊框

<details>
<summary>💡 提示：讓方法更穩健</summary>

- 只在影像外圍的一定比例內（例如外側 10～15%）尋找邊界，避免把內容中的強邊緣誤認為邊框
- 三個通道各自偵測，最後取最保守（裁最多）的邊界
- 每一邊（上/下/左/右）分開處理
</details>

**展示**：裁切前 vs. 裁切後，可以在裁切前的圖上用線畫出偵測到的邊界。

### 12.2 自動對比（Automatic contrasting）

**需要的觀念**：

- **直方圖（histogram）**：影像亮度值的分布。對比差的圖，直方圖擠在中間一小段
- **線性拉伸（contrast stretching）**：把 `[min, max]` 線性映射到 `[0, 1]`
  - 作業提示：用「所有通道中最暗的像素 → 0，最亮的像素 → 1」
  - 問題：一顆極端的雜訊點就會讓 min/max 失真 → 改用**百分位數**（例如 1% 和 99%）作為 min/max，更穩健
- **非線性映射**：
  - Gamma 校正：$I' = I^{\gamma}$
  - **直方圖均衡化（histogram equalization）**：讓輸出的直方圖盡量平坦；原理是用累積分布函數（CDF）當作映射函數
  - **CLAHE**（局部自適應直方圖均衡）：分區塊做均衡並限制對比放大，避免雜訊被過度放大

**注意**：三個通道要用**同一個**映射（線性拉伸時），否則會改變色彩平衡。如果要做非線性均衡化，考慮只對亮度通道做（例如轉到 HSV / Lab 色彩空間只調 V / L）。

**展示**：before / after ＋ 直方圖對照。

### 12.3 自動白平衡（Automatic white balance）

**需要的觀念**：

- **色彩恆常性**：人眼會自動「扣掉」光源顏色，相機不會。所以在偏黃的燈光下拍的照片看起來偏黃。
- 白平衡分兩步：
  1. **估計光源顏色**（困難）
  2. **補償**（簡單）：對每個通道乘上一個係數（von Kries 模型 / 對角矩陣），讓估計的光源變成中性灰／白
- 兩個經典的簡單估計法：
  - **Gray World**：假設整張圖的平均顏色應該是灰色 → 讓三個通道平均值相等
  - **White Patch（Max-RGB）**：假設最亮的點應該是白色 → 讓三個通道的最大值（或 99 百分位）相等

<details>
<summary>💡 提示：補償的公式長什麼樣</summary>

若估計的光源顏色為 $(L_R, L_G, L_B)$，希望它變成灰色 $(k, k, k)$，那每個通道的增益就是 $k / L_c$。$k$ 可以選三者平均，或選 G 通道（固定 G 不動）。
</details>

**注意**：兩種假設都可能失敗（例如一大片藍天時 Gray World 會讓天空變灰）。在網頁上討論你觀察到的失敗案例很加分。

### 12.4 更好的色彩映射（Better color mapping）

**需要的觀念**：

- Prokudin-Gorskii 的濾鏡的光譜響應，和現代 sRGB 的 R、G、B 原色**並不相同**；底片本身的感光特性也不同
- 所以「B 濾鏡底片 → sRGB 的 B 通道」是一個粗略假設
- 更一般的模型：每個輸出通道是三個輸入通道的**線性組合**

$$
\begin{bmatrix} R' \\ G' \\ B' \end{bmatrix} = M_{3\times3} \begin{bmatrix} R \\ G \\ B \end{bmatrix}
$$

**怎麼得到 $M$？**

- 方法一：手動試、根據觀察調整（例如發現綠色植物太藍）——可以但要說明理由
- 方法二（更有說服力）：找一張 LoC 已經**專業修復過的彩色版本**，和你的對齊結果配對像素，用**最小平方法**（`np.linalg.lstsq`）解出 $M$；再把同一個 $M$ 套到**其他**圖上，看是否泛化
- 也可以考慮在其他色彩空間（例如 Lab）中調整

**展示**：before / after，最好與 LoC 官方修復版並排。

### 12.5 更好的特徵（Better features）——修好 emir 的關鍵

**需要的觀念**：

- 不同濾鏡下的**亮度**可能不同，但物體的**邊緣位置**是一樣的
- 所以先把每個通道轉成「邊緣/梯度圖」，再對梯度圖做 NCC/L2

**梯度的計算**：

- 最基本：有限差分 $\partial_x I \approx I(x+1, y) - I(x, y)$
- **Sobel 運算子**：結合平滑與差分，對雜訊比較穩健
- 梯度大小：$|\nabla I| = \sqrt{(\partial_x I)^2 + (\partial_y I)^2}$
- 更進一步：**Canny 邊緣偵測**（會產生二值邊緣圖）

**整合到你的金字塔**：

- 在每一層級，先對兩張圖算梯度大小，再呼叫原本的 metric
- 或者每一層都用原本的流程，只是傳進去的不是原圖而是特徵圖
- 寫成一個 `feature_fn` 參數（例如 `identity` 或 `gradient_magnitude`）會很乾淨，也方便在網頁上做 RGB vs. gradient 的對照

<details>
<summary>💡 提示：為什麼梯度大小比單一方向的梯度好？</summary>

想想看：如果某條邊在 B 通道是「左暗右亮」，在 R 通道是「左亮右暗」，那 $\partial_x$ 的正負號會相反，NCC 會給出負相關。但梯度**大小**在兩個通道都是正的、而且在同一個位置有峰值。
</details>

> ⚠️ 再次提醒：即使你用了梯度特徵，網頁上仍然要展示**基本 RGB NCC/L2** 的結果與位移表，再展示改進後的版本。

### 12.6（可選）更好的變換模型

- 除了 (dx, dy)，再搜尋小角度旋轉、小幅縮放
- 搜尋空間從 2 維變 4 維，成本暴增 → coarse-to-fine 更加重要
- 可以先觀察：哪幾張圖在平移對齊之後，**某一側**對齊得好、**另一側**還有色邊？這就是旋轉/縮放的證據

### 12.7（可選）其他資料來源

- 天文影像（例如 Hubble、SDO 太陽觀測）常常是一個通道一個通道拍的
- 用你的演算法對齊並合成假色影像。作業要求：要展示**非平凡**的對齊與色彩校正

> 🧠 **學到的知識（B&W 整體）**：
> - 一個管線（pipeline）中每個步驟的**假設**是什麼、何時會失效
> - 影像增強（對比、白平衡）沒有唯一正解，評估往往需要視覺比較 + 客觀指標並用
> - 「改變表示法（raw pixel → gradient）」常常比「調參數」更能解決根本問題

### 12.8 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

12.5 的梯度特徵已經在 `align.py` 裡（`gradient_magnitude` + `align_pyramid(..., feature_fn=...)`），命令列用 `python code/main.py --feature grad` 或 `--ref g` 切換。其餘 12.1～12.4 放在 `enhance.py`，`s12_bells.py` 用 emir 串起整條管線並畫出 before / after 與直方圖。

實測（emir）：RGB NCC 的 R = (−205, 141) ❌；梯度 NCC 的 R = (40, 107) ✅；以 G 為基準時 R→G = (17, 57)，換算回 B 基準約 (41, 106) ✅。

> ⚠️ `detect_borders` 是啟發式方法：在 14 張圖上大致能去掉黑白邊與錯位色帶，但遇到靠近邊緣的大片亮天空（例如 harvesters 頂端）會多裁一些（最多裁到 `max_frac`，也就是 10%）。這正好可以寫進網頁的討論。
>
> 12.4 的 `fit_color_matrix` 在範例裡只用「自己 → 自己」驗證會解出單位矩陣；實際使用時請把 target 換成「與你的結果已對齊、同尺寸」的 LoC 官方修復版。12.6（旋轉/縮放）與 12.7（其他資料）屬於自由發揮，沒有附範例。

<details>
<summary>📄 <code>code/enhance.py</code></summary>

```python
"""enhance.py：Bells & Whistles —— 自動裁切、自動對比、白平衡、色彩映射。"""
import numpy as np
from skimage import color as skcolor, exposure


# ---------- 12.1 自動裁切 ----------
def _border_extent(profile_bad, max_frac):
    """profile_bad：從外往內排列的布林陣列（True = 像邊框）。回傳要裁掉幾列/行。"""
    n = int(len(profile_bad) * max_frac)
    bad = np.flatnonzero(profile_bad[:n])
    return int(bad[-1]) + 1 if bad.size else 0


def detect_borders(rgb, max_frac=0.1, extreme=0.05, dev_thr=0.3):
    """
    回傳 (top, bottom, left, right)：每一邊要裁掉的像素數。
    一列/一行被視為「邊框」若：
      (1) 任一通道的平均值接近純黑或純白（< extreme 或 > 1 - extreme），或
      (2) 任一通道的平均值和「該通道所有列/行平均的中位數」相差 > dev_thr
          ——內容區域三通道彼此一致、變化平緩；邊框和 np.roll 繞回來的色帶則會在
            某個通道突然變得很亮或很暗。
    只在外側 max_frac 比例內尋找，取該範圍內「最內側」的邊框列/行。
    """
    def bad_profile(axis):
        means = rgb.mean(axis=axis)                     # (N, 3)：每列/行、每通道的平均
        dev = np.abs(means - np.median(means, axis=0))  # 與中位數（代表內容）的差距
        return ((means.min(axis=1) < extreme) | (means.max(axis=1) > 1 - extreme)
                | (dev.max(axis=1) > dev_thr))

    rows = bad_profile(axis=1)                          # 每一列（沿 x 平均）
    cols = bad_profile(axis=0)                          # 每一行（沿 y 平均）
    top = _border_extent(rows, max_frac)
    bottom = _border_extent(rows[::-1], max_frac)
    left = _border_extent(cols, max_frac)
    right = _border_extent(cols[::-1], max_frac)
    return top, bottom, left, right


def auto_crop(rgb, **kw):
    t, b, l, r = detect_borders(rgb, **kw)
    h, w = rgb.shape[:2]
    return rgb[t:h - b, l:w - r], (t, b, l, r)


# ---------- 12.2 自動對比 ----------
def auto_contrast(rgb, low=1, high=99):
    """三通道共用同一個線性映射：第 low 百分位 → 0，第 high 百分位 → 1。"""
    lo, hi = np.percentile(rgb, [low, high])
    return np.clip((rgb - lo) / (hi - lo + 1e-8), 0, 1)


def auto_contrast_clahe(rgb, clip_limit=0.01):
    """只對 Lab 的 L（亮度）做 CLAHE，避免改變色相。"""
    lab = skcolor.rgb2lab(rgb)
    lab[..., 0] = exposure.equalize_adapthist(lab[..., 0] / 100, clip_limit=clip_limit) * 100
    return np.clip(skcolor.lab2rgb(lab), 0, 1)


# ---------- 12.3 自動白平衡 ----------
def white_balance(rgb, method="gray_world", pct=99):
    """
    gray_world ：讓三通道平均值相等
    white_patch：讓三通道第 pct 百分位相等（比 max 穩健）
    以 G 通道為基準（G 的增益 = 1）。
    """
    flat = rgb.reshape(-1, 3)
    if method == "gray_world":
        illum = flat.mean(axis=0)
    else:
        illum = np.percentile(flat, pct, axis=0)
    gains = illum[1] / (illum + 1e-8)
    return np.clip(rgb * gains, 0, 1), gains


# ---------- 12.4 色彩映射 ----------
def fit_color_matrix(src_rgb, target_rgb, n_samples=200_000, seed=0):
    """
    用最小平方法解 M (3x3) 與偏移 t (3,)，使 target ≈ src @ M.T + t。
    src、target 必須已經對齊且 shape 相同。
    """
    rng = np.random.default_rng(seed)
    X = src_rgb.reshape(-1, 3)
    Y = target_rgb.reshape(-1, 3)
    idx = rng.choice(len(X), size=min(n_samples, len(X)), replace=False)
    X1 = np.hstack([X[idx], np.ones((len(idx), 1))])  # 加一行常數項
    sol, *_ = np.linalg.lstsq(X1, Y[idx], rcond=None)  # (4, 3)
    return sol[:3].T, sol[3]


def apply_color_matrix(rgb, M, t=np.zeros(3)):
    return np.clip(rgb @ M.T + t, 0, 1)
```
</details>

<details>
<summary>📄 <code>code/s12_bells.py</code></summary>

```python
"""關卡十：Bells & Whistles 示範。執行：python code/s12_bells.py data/emir.tif"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import skimage.io as skio
from skimage import img_as_ubyte

from align import colorize, load_plate, gradient_magnitude
from enhance import (detect_borders, auto_crop, auto_contrast, auto_contrast_clahe,
                     white_balance, fit_color_matrix, apply_color_matrix)

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/emir.tif")
im = load_plate(path)
save = lambda name, x: skio.imsave(f"out/{path.stem}_{name}.jpg", img_as_ubyte(np.clip(x, 0, 1)))

# 12.5 更好的特徵：RGB NCC vs 梯度 NCC（vs 以 G 為基準）
rgb_basic, s1 = colorize(im)
rgb_grad, s2 = colorize(im, feature_fn=gradient_magnitude)
_, s3 = colorize(im, ref="g")
print("RGB NCC     :", s1)
print("gradient NCC:", s2)
print("ref = G     :", s3)
save("basic", rgb_basic); save("grad", rgb_grad)

# 12.1 自動裁切
t, b, l, r = detect_borders(rgb_grad)
cropped, _ = auto_crop(rgb_grad)
print("裁切 (top, bottom, left, right) =", (t, b, l, r))
save("cropped", cropped)

# 12.2 自動對比
contrast = auto_contrast(cropped, 1, 99)
clahe = auto_contrast_clahe(cropped)
save("contrast", contrast); save("clahe", clahe)

# 12.3 自動白平衡
wb_gw, gains_gw = white_balance(contrast, "gray_world")
wb_wp, gains_wp = white_balance(contrast, "white_patch")
print("gray world gains :", gains_gw.round(3))
print("white patch gains:", gains_wp.round(3))
save("wb_grayworld", wb_gw); save("wb_whitepatch", wb_wp)

# 12.4 色彩映射：示範用「自己 → 自己」驗證 lstsq 會解出單位矩陣。
# 實際使用時把 target 換成「已對齊、同尺寸」的 LoC 官方修復彩色版。
M, t_off = fit_color_matrix(contrast, contrast)
print("M (應接近單位矩陣):\n", M.round(3), "\noffset:", t_off.round(3))

# Before / after 並排 + 直方圖
fig, axes = plt.subplots(2, 4, figsize=(18, 9))
for ax, (title, x) in zip(axes[0], [("basic RGB NCC", rgb_basic), ("gradient + crop", cropped),
                                    ("+ contrast", contrast), ("+ white patch", wb_wp)]):
    ax.imshow(x); ax.set_title(title); ax.axis("off")
for ax, (title, x) in zip(axes[1], [("hist: cropped", cropped), ("hist: contrast", contrast),
                                    ("hist: CLAHE", clahe), ("hist: white patch", wb_wp)]):
    for c, col in enumerate("rgb"):
        ax.hist(x[..., c].ravel()[::50], bins=128, range=(0, 1), color=col, alpha=0.4)
    ax.set_title(title)
plt.tight_layout()
plt.savefig(f"out/{path.stem}_bells.jpg", dpi=70)
plt.show()
```
</details>

---

## 13. 關卡十一：網頁報告與繳交

### 13.1 網頁的定位

作業的說法：「想像你在寫一篇部落格文章給朋友看」。要**好讀、有組織、視覺上吸引人**。介紹每個新觀念時，順便展示它帶來的改進。

### 13.2 建議的章節結構（對應評分項目）

1. **Introduction**
   - Prokudin-Gorskii 的背景一兩段、問題定義、一張原始底片圖
2. **Approach: Single-scale alignment**（評分 60% 裡的報告分）
   - 切割三通道（附圖）
   - 直接疊合的 baseline（附 color fringing 的圖）
   - L2 與 NCC 的公式與直覺、為什麼 NCC 對亮度變化較穩健
   - 平移與邊界處理（為什麼要裁掉邊框才算分）
   - 窮舉搜尋的流程
   - **結果**：3 張 JPG，L2 與 NCC 各自的結果與位移
3. **Approach: Multi-scale pyramid**（評分 40% 裡的報告分：要求「walking through each step carefully」）
   - 為什麼需要：TIF 的大小、位移量、單尺度的時間估算
   - 降採樣與 anti-aliasing 的說明（可以附一張「直接取樣 vs. 先模糊再取樣」的對照）
   - 金字塔示意圖、coarse-to-fine 流程
   - 參數選擇與理由（層數、每層視窗、裁切比例）
   - 執行時間
4. **Results**
   - 所有 14 張官方圖 + 3 張以上自選圖
   - 每張圖標註 G、R 位移（也可另做一張總表）
5. **Failure analysis**
   - 哪張失敗、放大局部、解釋是哪個假設被打破
6. **Bells & Whistles**
   - 每一項：動機 → 方法 → before / after
7. **Conclusion / What I learned**

### 13.3 製作與部署

- 最簡單：手寫一個 `index.html`（加一點 CSS），圖片放在同 repo 的 `images/` 資料夾
- 部署：GitHub Pages（建立 repo → Settings → Pages → 選分支）
- 網頁用的圖片建議另外壓縮（例如寬度縮到 1000～1500 px 的 JPG），避免網頁載入過慢
- 如果有 before/after 滑桿、hover 切換等互動效果，記得在 PDF 中註明（PDF 無法呈現）

### 13.4 繳交結構

```
submission.zip
├─ code/
│  ├─ main.py          # 或 main.ipynb
│  ├─ align.py         # 可選
│  └─ README.txt
└─ web/
   └─ page.pdf         # 瀏覽器「列印 → 存成 PDF」，開啟「頁首與頁尾」讓 URL 出現在 PDF 上
```

- 只能上傳一個 zip，最大 100 MB、最多 256 個檔案
- **code/ 裡不要放任何圖片**
- 程式碼**不要**公開放在網路上（網頁 repo 和程式碼要分開，或確保網頁 repo 裡沒有程式碼）
- 網頁 URL：同時交到 Google Form（課程 gallery）與 Gradescope

### 13.5 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

`make_web_images.py` 把 `out/` 的結果縮成寬度 ≤ 1200 px 放進 `web/images/`，並把位移 CSV 轉成 HTML 表格 `web/offsets_table.html`（直接貼進網頁）。`index.html` 是可以直接改的骨架，章節對應 13.2，用 MathJax 顯示公式。

<details>
<summary>📄 <code>code/make_web_images.py</code></summary>

```python
"""關卡十一：產生網頁用的縮圖與位移表 HTML。
執行：python code/make_web_images.py out/offsets_ncc_rgb_refb.csv"""
import csv
import sys
from pathlib import Path

import skimage.io as skio
from skimage import img_as_float, img_as_ubyte
from skimage.transform import rescale

MAX_W = 1200
csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else "out/offsets_ncc_rgb_refb.csv")
web = Path("web/images")
web.mkdir(parents=True, exist_ok=True)

# 1. 把 out/ 的結果縮到寬度 <= 1200 px
for f in sorted(Path("out").glob("*.jpg")):
    img = img_as_float(skio.imread(f))
    if img.shape[1] > MAX_W:
        img = rescale(img, MAX_W / img.shape[1], channel_axis=2, anti_aliasing=True)
    skio.imsave(web / f.name, img_as_ubyte(img))
print("縮圖已存到", web)

# 2. 把位移 CSV 轉成 HTML 表格（貼進 index.html）
with open(csv_path) as fh:
    rows = list(csv.DictReader(fh))
lines = ["<table>", "  <tr><th>image</th><th>method</th><th>G (dx, dy)</th>"
         "<th>R (dx, dy)</th><th>time (s)</th></tr>"]
for r in rows:
    lines.append(f"  <tr><td>{r['image']}</td><td>{r['method']}</td>"
                 f"<td>({r['g_dx']}, {r['g_dy']})</td><td>({r['r_dx']}, {r['r_dy']})</td>"
                 f"<td>{r['time_s']}</td></tr>")
lines.append("</table>")
Path("web/offsets_table.html").write_text("\n".join(lines), encoding="utf-8")
print("表格已存到 web/offsets_table.html")
```
</details>

<details>
<summary>📄 <code>web/index.html</code>（網頁骨架）</summary>

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS180 Project 1 – Colorizing the Prokudin-Gorskii Collection</title>
  <script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] } };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js" defer></script>
  <style>
    body { max-width: 960px; margin: 0 auto; padding: 24px 16px; font: 17px/1.65 system-ui, sans-serif; color: #222; }
    h1 { font-size: 2rem; margin-bottom: 0; }
    h2 { margin-top: 2.5rem; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
    img { max-width: 100%; height: auto; display: block; }
    figure { margin: 1rem 0; }
    figcaption { font-size: 0.9rem; color: #666; text-align: center; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
    th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: center; }
    th { background: #f5f5f5; }
    code { background: #f3f3f3; padding: 1px 4px; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>Colorizing the Prokudin-Gorskii Collection</h1>
  <p>CS180 Project 1 · Your Name</p>

  <h2>1. Introduction</h2>
  <p>Sergei Prokudin-Gorskii photographed the Russian Empire (1909–1915) by exposing three
     black-and-white plates through blue, green and red filters. The goal of this project is to
     split each glass plate into its B, G, R channels, find the (x, y) offsets that align G and R to B,
     and stack them into a single color image.</p>
  <figure><img src="images/cathedral_baseline.jpg" alt="raw plate stacked without alignment">
    <figcaption>Stacking the three channels without alignment produces color fringing.</figcaption></figure>

  <h2>2. Single-scale alignment</h2>
  <h3>2.1 Metrics</h3>
  <p>L2 (SSD): $\sum (A-B)^2$, lower is better. NCC:
     $\frac{\sum (a-\bar a)(b-\bar b)}{\|a-\bar a\|\,\|b-\bar b\|}$, higher is better, and invariant to
     $B = \alpha A + \beta$.</p>
  <h3>2.2 Borders</h3>
  <p>Scores are computed only on the interior (10% cropped from every side) so the plate borders and the
     wrap-around from <code>np.roll</code> do not dominate.</p>
  <h3>2.3 Exhaustive search</h3>
  <p>Search every (dx, dy) in [−15, 15]² and keep the best score.</p>
  <h3>2.4 Results</h3>
  <div class="grid">
    <figure><img src="images/cathedral_single_ncc.jpg" alt=""><figcaption>cathedral · G (2, 5) · R (3, 12)</figcaption></figure>
    <figure><img src="images/monastery_single_ncc.jpg" alt=""><figcaption>monastery · G (2, −3) · R (2, 3)</figcaption></figure>
    <figure><img src="images/tobolsk_single_ncc.jpg" alt=""><figcaption>tobolsk · G (3, 3) · R (3, 6)</figcaption></figure>
  </div>

  <h2>3. Multi-scale pyramid</h2>
  <p>Why it is needed, how downsampling with anti-aliasing works, the coarse-to-fine loop,
     parameter choices and running time.</p>

  <h2>4. Results (all images)</h2>
  <!-- 貼上 web/offsets_table.html 的內容 -->
  <div class="grid">
    <figure><img src="images/church_pyramid_ncc_rgb_refb.jpg" alt=""><figcaption>church · G (4, 25) · R (−4, 58)</figcaption></figure>
    <!-- 其餘圖片依此類推 -->
  </div>

  <h2>5. Failure analysis: emir</h2>
  <div class="pair">
    <figure><img src="images/emir_basic.jpg" alt=""><figcaption>RGB NCC: R fails</figcaption></figure>
    <figure><img src="images/emir_grad.jpg" alt=""><figcaption>Gradient NCC: fixed</figcaption></figure>
  </div>

  <h2>6. Bells &amp; Whistles</h2>
  <p>For each: motivation → method → before / after.</p>

  <h2>7. What I learned</h2>
  <p>…</p>
</body>
</html>
```
</details>

<details>
<summary>🖥️ 部署到 GitHub Pages 與打包繳交（bash）</summary>

```bash
# 1. 網頁（只放 web/，不要放程式碼）
cd web
git init && git add index.html images/
git commit -m "project 1 page"
git branch -M main
git remote add origin https://github.com/<你的帳號>/cs180-proj1.git
git push -u origin main
# 到 GitHub repo → Settings → Pages → Branch: main / root

# 2. 瀏覽器開啟網頁 → 列印 → 存成 PDF（勾選頁首與頁尾）→ 存成 web/page.pdf

# 3. 打包（code/ 裡不能有圖片）
cd ..
mkdir -p submission/code submission/web
cp code/*.py code/README.txt submission/code/
cp web/page.pdf submission/web/
(cd submission && zip -r ../submission.zip code web)
unzip -l submission.zip   # 檢查內容與大小（< 100 MB）
```
</details>

---

## 14. 最終檢查清單

### 程式

- [ ] 讀進來立刻轉 float，JPG 與 TIF 都能處理
- [ ] 三通道切割 shape 一致
- [ ] L2 與 NCC 都有實作、都能切換
- [ ] 計分時忽略邊框
- [ ] 單尺度窮舉搜尋能正確對齊 cathedral、monastery、tobolsk
- [ ] 金字塔自己實作（含適當的降採樣／抗 aliasing），沒用到現成 pyramid / registration 函式
- [ ] 每張 TIF < 1 分鐘
- [ ] 所有圖片使用**同一組參數**
- [ ] 印出每張圖的 G、R 位移 `(x, y)`
- [ ] 輸出存成 JPG
- [ ] `main.py` 一鍵重現；`README.txt` 寫清楚執行方式
- [ ] 程式碼有適當註解，助教能找到核心實作

### 網頁

- [ ] 單尺度：3 張 JPG 結果（L2 / NCC）＋ 位移
- [ ] 金字塔：全部 14 張官方圖結果 ＋ 位移表（基本 RGB NCC/L2）
- [ ] 自選 3 張以上 LoC 圖片的結果 ＋ 位移
- [ ] 失敗案例與原因分析
- [ ] 方法說明：公式、圖示、每一步的動機
- [ ] Bells & Whistles（如有）：動機、方法、before / after
- [ ] 網頁已部署且公開可存取

### 繳交

- [ ] zip 結構正確、< 100 MB、code 中無圖片
- [ ] `web/page.pdf` 頁首/頁尾含 URL
- [ ] Google Form 已填
- [ ] Gradescope 已上傳並附上網頁 URL

### 📦 本節完整範例程式碼

> 建議先自己完成本節，卡住或寫完後再展開對照。

交件前執行 `python code/tests.py`：檢查 metric、平移方向、降採樣、**合成位移能否被找回**（包含在 church.tif 上平移 (120, −90) 這種大位移），以及三張 JPG 的位移是否在預期值 ±1 px 內。

<details>
<summary>📄 <code>code/tests.py</code></summary>

```python
"""最終自我檢查。執行：python code/tests.py"""
import time

import numpy as np

from align import (load_plate, split_bgr, shift, crop_interior, l2_score, ncc_score,
                   align_single_scale, align_pyramid, downsample, build_pyramid)

rng = np.random.default_rng(0)

# 1. metric
a = rng.random((64, 64))
assert np.isclose(ncc_score(a, 2 * a + 0.3), 1.0)
assert np.isclose(ncc_score(a, -a), -1.0)
assert l2_score(a, a) == 0 and l2_score(a, a + 0.3) < -100

# 2. shift / crop 方向
img = np.zeros((10, 10)); img[2, 3] = 1
assert tuple(np.argwhere(shift(img, 4, 1) == 1)[0]) == (3, 7)
assert crop_interior(np.ones((400, 300)), 0.1).shape == (320, 240)

# 3. downsample / pyramid
assert downsample(np.ones((101, 64))).shape == (50, 32)
assert all(min(p.shape) >= 150 for p in build_pyramid(np.ones((3200, 3700))))

# 4. 已知位移能否找回來：把 B 平移 (dx, dy) 當作 moving，應該找回 (-dx, -dy)
b, g, r = split_bgr(load_plate("data/cathedral.jpg"))
for dx, dy in [(5, -7), (-3, 12)]:
    assert align_single_scale(shift(b, dx, dy), b) == (-dx, -dy)
    assert align_pyramid(shift(b, dx, dy), b) == (-dx, -dy)

b, g, r = split_bgr(load_plate("data/church.tif"))
t0 = time.perf_counter()
assert align_pyramid(shift(b, 120, -90), b) == (-120, 90)
print(f"大位移合成測試 OK（{time.perf_counter() - t0:.1f}s）")

# 5. 作業 JPG 的位移
expected = {"cathedral": ((2, 5), (3, 12)), "monastery": ((2, -3), (2, 3)),
            "tobolsk": ((3, 3), (3, 6))}
for name, (eg, er) in expected.items():
    b, g, r = split_bgr(load_plate(f"data/{name}.jpg"))
    got = (align_single_scale(g, b), align_single_scale(r, b))
    assert all(abs(u - v) <= 1 for p, q in zip(got, (eg, er)) for u, v in zip(p, q)), (name, got)
print("全部測試通過 ✅")
```
</details>

---

## 15. 自我測驗

做完之後，試著不看資料回答下列問題。答案折疊在下面——先自己想。

**Q1.** 為什麼 `uint8` 影像在計算 L2 之前必須轉換型別？

<details><summary>答案</summary>

`uint8` 減法會溢位（wrap around），例如 `10 - 20 = 246`，平方之後的值也會錯。轉成 float 後才能得到正確的差值。另外轉成 `[0,1]` 也讓 JPG 與 TIF 能共用相同參數。
</details>

**Q2.** 若 $B = 3A + 0.5$，L2 和 NCC 各會給出什麼結果？為什麼？

<details><summary>答案</summary>

L2 會很大（因為數值差很多），即使結構完全相同。NCC 等於 1，因為減去平均消除了 $+0.5$，除以 norm 消除了 $\times 3$。
</details>

**Q3.** 為什麼計算分數時要裁掉邊界？裁切寬度與搜尋範圍有什麼關係？

<details><summary>答案</summary>

(1) 底片邊框的強烈對比和雜訊在三通道不一致，會主導分數、讓演算法去對齊邊框而非內容。(2) `np.roll` 會讓平移出去的像素繞回另一側，形成錯誤的邊界帶，寬度等於位移量。裁切寬度要大於搜尋範圍，才能保證這條錯誤帶永遠被排除。
</details>

**Q4.** 在金字塔中，為什麼降採樣前要先模糊？

<details><summary>答案</summary>

依取樣定理，降低取樣率前必須先去除超過新 Nyquist 頻率的高頻成分，否則高頻會折疊成假的低頻圖樣（aliasing），在小圖上產生原圖不存在的結構，可能誤導粗層級的對齊。
</details>

**Q5.** 粗一層找到的位移為 (dx, dy)，回到下一層時要怎麼用？為什麼下一層只需要小視窗？

<details><summary>答案</summary>

乘以 2 得到這一層的初始估計，然後只在其附近搜尋。粗層一個像素對應本層兩個像素，所以粗層的誤差（約 ±1 px）放大後只有約 ±2 px，小視窗就足以修正。
</details>

**Q6.** 金字塔方法的主要風險是什麼？

<details><summary>答案</summary>

如果最粗層找錯（例如重複紋理、資訊太少、亮度關係不一致），之後每一層都只在錯誤答案附近小範圍搜尋，無法跳出來修正。
</details>

**Q7.** 為什麼 emir.tif 用 RGB NCC 會失敗？有哪兩種常見修正？

<details><summary>答案</summary>

埃米爾的衣服在不同濾鏡下亮度差異極大且非線性（在 B 亮、在 R 暗），違反 NCC「通道間亮度線性相關」的假設。修正：(1) 改以 G 為基準通道；(2) 改用梯度/邊緣特徵比較結構而非亮度。
</details>

**Q8.** 為什麼 R 的位移通常比 G 的大？

<details><summary>答案</summary>

三張曝光是依序（B → G → R）拍攝的，在拍攝期間相機/底片/被攝物持續有微小移動，所以離 B 越遠（時間上越晚）的那張累積的位移通常越大。
</details>

**Q9.** Gray World 白平衡的假設是什麼？在什麼情況會失敗？

<details><summary>答案</summary>

假設場景整體的平均反射率是中性灰色。當畫面被大面積單一顏色佔據（藍天、草地、海）時會失敗，把那個顏色錯誤地「校正」成灰色。
</details>

**Q10.** 計算梯度特徵時，為什麼用梯度**大小**比單一方向的梯度更適合跨通道對齊？

<details><summary>答案</summary>

同一條邊在不同通道中可能明暗方向相反，方向性梯度的符號會相反、造成負相關；梯度大小只看「這裡是否有邊」，在各通道都是正值且位置一致。
</details>

---

## 16. 延伸閱讀

- Library of Congress 的說明：*The Making of the Prokudin-Gorskii Color Images*：<http://www.loc.gov/exhibits/empire/making.html>
- Szeliski, *Computer Vision: Algorithms and Applications*（免費線上版）<https://szeliski.org/Book/>
  - §2.3.2 Color（白平衡）
  - §3.5 Pyramids and wavelets（影像金字塔）
  - §9.1 Translational alignment（平移對齊、SSD、NCC、階層式搜尋）
- Wikipedia：Color balance、Histogram equalization、Aliasing、Sobel operator
- NumPy Broadcasting：<https://numpy.org/doc/stable/user/basics.broadcasting.html>
- Python 效能小技巧：<https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops>

---

### 建議的時程（參考）

| 天數 | 目標 |
|---|---|
| Day 1 | 關卡 1～5：JPG 單尺度對齊完成 |
| Day 2 | 關卡 6～7：金字塔、全部 TIF 跑完且每張 < 1 分鐘 |
| Day 3 | 關卡 8～9：失敗分析、挑選並處理自選圖片 |
| Day 4–5 | 關卡 10：Bells & Whistles（CS280A 必做） |
| Day 6 | 關卡 11：網頁撰寫、部署、PDF、繳交 |

祝順利！卡住的時候，先回到「用眼睛看結果」與「最小可重現案例」（例如在一張小圖上手動平移已知量，看你的演算法能不能找回來）——這是最有效的除錯方法。
