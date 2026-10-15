CS180 Project 1 - Prokudin-Gorskii Colorization

Requirements: Python 3.10+, numpy, scipy, scikit-image, matplotlib
    python3 -m venv .venv && source .venv/bin/activate
    pip install numpy scipy scikit-image matplotlib

Layout (run everything from the project root, i.e. the folder containing data/):
    data/            input plates (.jpg / .tif)
    code/align.py    core: split, L2/NCC, shift, single-scale search, pyramid
    code/main.py     entry point

Run:
    python code/main.py                    # all images, RGB NCC, reference = B
    python code/main.py --metric l2        # L2 instead of NCC
    python code/main.py --feature grad     # gradient-magnitude features (fixes emir)
    python code/main.py --only emir        # a subset
    python code/main.py --ref g            # align B and R to G instead of B
    python code/main.py --data data --out out   # input / output folders

Output:
    out/<name>_<method>_<metric>_<feature>_ref<b|g>.jpg
    out/offsets_<metric>_<feature>_ref<b|g>.csv   (G/R offsets as (dx, dy) and runtime)

Parameters (same for every image): crop 10% per side when scoring,
pyramid coarsest short side >= 150 px, coarse window +-15, fine window +-3.

