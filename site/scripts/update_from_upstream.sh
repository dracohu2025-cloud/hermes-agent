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

echo "[1/5] 获取官方 source site 最新代码"
git fetch upstream main
git merge --ff-only "upstream/main"

cd "${REPO_ROOT}/site"

if [ ! -d "${REPO_ROOT}/site/node_modules" ]; then
  echo "[2/5] 安装站点依赖"
  npm ci
else
  echo "[2/5] 站点依赖已存在，跳过安装"
fi

echo "[3/5] 增量同步中文站"
npm run sync:docs

echo "[4/5] 结构校验"
npm run check:docs-parity

echo "[5/5] 构建中文站"
npm run build

echo
echo "完成。请抽查首页、Quickstart、Developer Guide、Reference，然后再决定是否提交和部署。"
