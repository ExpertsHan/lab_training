#!/usr/bin/env bash
# deploy_web.sh：把 web/（只有 index.html 與 images/，不含程式碼）推到獨立的 GitHub Pages repo。
#
# 事前：到 https://github.com/new 建一個「空的」Public repo（不要勾 README），例如 cs180-proj1
# 用法（在 project1/ 底下）：
#   bash deploy_web.sh https://github.com/<帳號>/cs180-proj1.git
# 推完後：repo → Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save
# 網址會是 https://<帳號>.github.io/cs180-proj1/
set -euo pipefail

REMOTE="${1:?用法: bash deploy_web.sh <repo 的 git URL>}"
SRC="$(cd "$(dirname "$0")" && pwd)/web"
# 放在 lab_training 以外，避免變成巢狀 git repo
DEST="${DEPLOY_DIR:-$HOME/Documents/cs180-proj1-web}"

mkdir -p "$DEST"
rsync -a --delete --exclude '.git' --exclude '.DS_Store' --exclude 'page.pdf' \
      --include 'index.html' --include 'images/***' --exclude '*' \
      "$SRC/" "$DEST/"
touch "$DEST/.nojekyll"   # 讓 GitHub Pages 原樣提供檔案

cd "$DEST"
if [ ! -d .git ]; then
  git init -q
  git branch -M main
  git remote add origin "$REMOTE"
fi
git add -A
git commit -q -m "Update project 1 page" || echo "（沒有變更需要提交）"
git push -u origin main

echo
echo "已推送到 ${REMOTE}（本地資料夾：${DEST}）"
echo "第一次部署請到 repo → Settings → Pages，Branch 選 main / (root)。"
