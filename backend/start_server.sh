#!/bin/bash
# 后端服务启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
source ai-teacher-platform-backend/bin/activate

# 检查数据库连接
echo "🔍 检查数据库连接..."
python -c "from src.database import DATABASE_URL; print(f'数据库: {DATABASE_URL[:30]}...')" 2>&1

# 启动服务
echo ""
echo "🚀 启动后端服务..."
echo "   访问地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   按 Ctrl+C 停止服务"
echo ""

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

