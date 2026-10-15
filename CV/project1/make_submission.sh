#!/usr/bin/env bash
# make_submission.sh：把網頁印成 PDF，並打包成 submission.zip。
#
# 用法（在 project1/ 底下，網頁部署完成後）：
#   bash make_submission.sh https://<帳號>.github.io/cs180-proj1/
# 不給網址時會改用本地的 web/index.html 產生 PDF（PDF 頁首頁尾就不會是公開網址）。
set -euo pipefail
cd "$(dirname "$0")"

URL="${1:-file://$PWD/web/index.html}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 1. 網頁 → web/page.pdf（headless Chrome 預設會印出頁首頁尾，含網址）
"$CHROME" --headless=new --disable-gpu --virtual-time-budget=15000 \
          --print-to-pdf="$PWD/web/page.pdf" "$URL" 2>/dev/null
echo "PDF：web/page.pdf（來源 ${URL}）"

# 2. 組出 submission/：code 只放程式與 README.txt，不能有圖片
rm -rf submission submission.zip
mkdir -p submission/code submission/web
cp code/align.py code/main.py code/make_web_images.py submission/code/
cp code/README.md submission/code/README.txt
cp web/page.pdf submission/web/

(cd submission && zip -qr ../submission.zip code web -x '*.DS_Store')

# 3. 檢查
unzip -l submission.zip
SIZE=$(du -k submission.zip | cut -f1)
if find submission/code -iname '*.jpg' -o -iname '*.png' -o -iname '*.tif' | grep -q .; then
  echo "⚠️ code/ 裡有圖片，請移除"; exit 1
fi
[ "$SIZE" -lt 100000 ] && echo "✅ submission.zip ${SIZE} KB（< 100 MB）" || { echo "⚠️ 超過 100 MB"; exit 1; }
