#!/usr/bin/env bash
# =============================================================
#  咫尺天涯 · 一键推送到 GitHub
#  用法：在 Git Bash 中执行  bash push-to-github.sh
#  前提：已在 GitHub 上创建好空仓库
# =============================================================
set -e

REPO_NAME="${1:-zhichi-tianya-platform}"
GITHUB_USER="${2:-}"
COMMIT_MSG="${3:-feat: 咫尺天涯社交平台 毕业设计提交}"

if [ -z "$GITHUB_USER" ]; then
  read -rp "请输入你的 GitHub 用户名: " GITHUB_USER
fi

echo "==> 初始化仓库"
if [ ! -d .git ]; then
  git init
fi

git add .
git commit -m "$COMMIT_MSG" || echo "(没有需要提交的改动)"
git branch -M main

echo "==> 关联远程仓库"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "==> 推送到 GitHub（密码处请粘贴 Personal Access Token）"
git push -u origin main

echo ""
echo "✅ 完成！仓库地址： https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "   下一步：按《部署指南.md》选择 PythonAnywhere（推荐）或 Render 上线。"
