#!/bin/bash
# 党建AI智能平台 - 部署打包脚本

set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DIST_DIR="$SCRIPT_DIR"
FRONTEND_DIST="$DIST_DIR/frontend"
BACKEND_DIST="$DIST_DIR/backend"

echo "📦 开始打包部署文件..."
echo "项目根目录: $PROJECT_ROOT"
echo "部署目录: $DIST_DIR"

# 清理旧的部署文件
echo "🧹 清理旧文件..."
rm -rf "$FRONTEND_DIST"
rm -rf "$BACKEND_DIST"
mkdir -p "$BACKEND_DIST"

# 1. 前端构建
echo "🔨 构建前端..."
cd "$PROJECT_ROOT/frontend"
npm run build
cp -r dist "$FRONTEND_DIST"

# 2. 后端打包（排除不必要的文件）
echo "📦 打包后端..."
cd "$PROJECT_ROOT/backend"

# 创建目录结构
mkdir -p "$BACKEND_DIST"/{src,alembic,static,uploads}

# 配置文件放在与 backend 同级的位置
mkdir -p "$DIST_DIR/configs"

# 复制源代码（排除缓存和测试文件）
rsync -av --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='*.pyo' \
          --exclude='.pytest_cache' \
          --exclude='htmlcov' \
          --exclude='.coverage' \
          --exclude='tests' \
          --exclude='.ruff_cache' \
          src/ "$BACKEND_DIST/src/"

# 复制 alembic
rsync -av --exclude='__pycache__' \
          --exclude='*.pyc' \
          alembic/ "$BACKEND_DIST/alembic/"
cp alembic.ini "$BACKEND_DIST/"

# 复制配置文件（与 backend 同级，代码期望的位置）
cp -r "$PROJECT_ROOT/configs"/* "$DIST_DIR/configs/"
cp -r "$PROJECT_ROOT/backend/static"/* "$BACKEND_DIST/static/" 2>/dev/null || true

# 复制必要文件
cp requirements.txt "$BACKEND_DIST/"
cp .env.example "$BACKEND_DIST/"
cp init_db.py "$BACKEND_DIST/" 2>/dev/null || true
cp init_course_data.sql "$BACKEND_DIST/" 2>/dev/null || true
cp start_server.sh "$BACKEND_DIST/" 2>/dev/null || true

# 复制生产环境配置
echo "📝 应用生产环境配置..."
cp "$DIST_DIR/.env.production" "$BACKEND_DIST/.env"

echo ""
echo "✅ 打包完成！"
echo ""
echo "部署文件位置："
echo "  前端: $FRONTEND_DIST"
echo "  后端: $BACKEND_DIST"
echo "  配置: $DIST_DIR/configs"
echo ""
echo "部署到服务器："
echo "  运行: ./dist/deploy.sh"
