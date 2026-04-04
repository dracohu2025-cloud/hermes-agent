#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"

if [ -n "$(git status --porcelain)" ]; then
  echo "工作区不干净，请先提交、暂存或清理本地改动后再执行。"
  exit 1
fi

if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream "https://github.com/NousResearch/hermes-agent.git"
fi

echo "[1/6] 获取官方 source site 最新代码"
git fetch upstream main
git merge --ff-only "upstream/main"

cd "${REPO_ROOT}/site"

echo "[2/6] 同步中文站结构文件"
python scripts/sync_localized_site_config.py

if [ ! -d "${REPO_ROOT}/site/node_modules" ]; then
  echo "[3/6] 安装站点依赖"
  npm ci
else
  echo "[3/6] 站点依赖已存在，跳过安装"
fi

echo "[4/6] 增量同步中文站"
npm run sync:docs -- --prune --record-watch-state

echo "[5/6] 结构校验"
npm run check:docs-parity

echo "[6/6] 构建中文站"
npm run build

echo
echo "完成。请抽查首页、Quickstart、Developer Guide、Reference，然后再决定是否提交和部署。"
