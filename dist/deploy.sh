#!/bin/bash
# 党建AI智能平台 - 文件上传脚本

set -e

# 服务器配置
SERVER_HOST="39.97.6.179"
SERVER_USER="root"
SERVER_PASS="Hcy20251007"
SERVER_DIR="/home/party-building"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIST="$SCRIPT_DIR/frontend"
BACKEND_DIST="$SCRIPT_DIR/backend"

echo "📤 开始上传文件到 $SERVER_HOST..."
echo "目标目录: $SERVER_DIR"

# 1. 先执行构建
echo ""
echo "📦 构建项目..."
"$SCRIPT_DIR/build.sh"

# 2. 创建服务器目录
echo ""
echo "📁 创建服务器目录..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "mkdir -p $SERVER_DIR/frontend $SERVER_DIR/backend/uploads $SERVER_DIR/configs"

# 3. 上传前端文件
echo ""
echo "📤 上传前端文件..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -r "$FRONTEND_DIST"/* "$SERVER_USER@$SERVER_HOST:$SERVER_DIR/frontend/"

# 4. 上传后端文件
echo ""
echo "📤 上传后端文件..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -r "$BACKEND_DIST" "$SERVER_USER@$SERVER_HOST:$SERVER_DIR/"

# 5. 上传配置文件
echo ""
echo "📤 上传配置文件..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -r "$SCRIPT_DIR/configs"/* "$SERVER_USER@$SERVER_HOST:$SERVER_DIR/configs/"

echo ""
echo "✅ 上传完成！"
echo ""
echo "文件位置："
echo "  前端: $SERVER_DIR/frontend"
echo "  后端: $SERVER_DIR/backend"
echo "  配置: $SERVER_DIR/configs"
