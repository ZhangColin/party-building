#!/bin/bash
# ============================================================
# 测试数据库初始化脚本
# 用途：创建独立的测试数据库，保护开发数据
# ============================================================

set -e  # 遇到错误立即退出

echo "🔧 设置测试数据库环境..."

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 数据库配置
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-password}"
TEST_DB_NAME="ai_teacher_platform_test"

echo -e "${YELLOW}⚠️  注意：这将在 MySQL 中创建测试数据库 '${TEST_DB_NAME}'${NC}"
echo -e "${YELLOW}⚠️  测试数据库独立于开发数据库，测试数据不会影响开发环境${NC}"
read -p "是否继续？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 已取消${NC}"
    exit 0
fi

# 检查 MySQL 连接
echo "📡 检查 MySQL 连接..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" &> /dev/null; then
    echo -e "${RED}❌ 无法连接到 MySQL，请检查配置${NC}"
    echo "  DB_HOST: $DB_HOST"
    echo "  DB_PORT: $DB_PORT"
    echo "  DB_USER: $DB_USER"
    exit 1
fi

echo -e "${GREEN}✅ MySQL 连接成功${NC}"

# 创建测试数据库（如果不存在）
echo "🗄️  创建测试数据库 '${TEST_DB_NAME}'..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS ${TEST_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

echo -e "${GREEN}✅ 测试数据库已创建${NC}"

# 运行数据库迁移
echo "📋 运行数据库迁移..."
cd "$(dirname "$0")/.."

# 加载测试环境变量
export $(cat .env.test | grep -v '^#' | xargs)

# 运行 Alembic 迁移
if command -v alembic &> /dev/null; then
    alembic upgrade head
    echo -e "${GREEN}✅ 数据库迁移完成${NC}"
else
    echo -e "${YELLOW}⚠️  Alembic 未安装，跳过迁移${NC}"
    echo "   安装方法: pip install alembic"
fi

# 创建测试数据
echo "👤 创建测试用户..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "${TEST_DB_NAME}" <<EOF
-- 插入测试管理员用户
INSERT INTO users (id, username, email, password_hash, is_admin, created_at)
VALUES (
    UUID(),
    'test_admin',
    'admin@test.com',
    '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj9SjKE.f7.' /* password: admin123 */,
    true,
    NOW()
) ON DUPLICATE KEY UPDATE id=id;

-- 插入测试普通用户
INSERT INTO users (id, username, email, password_hash, is_admin, created_at)
VALUES (
    UUID(),
    'test_user',
    'user@test.com',
    '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj9SjKE.f7.' /* password: password123 */,
    false,
    NOW()
) ON DUPLICATE KEY UPDATE id=id;
EOF

echo -e "${GREEN}✅ 测试用户已创建${NC}"
echo ""
echo "🎉 测试数据库设置完成！"
echo ""
echo "📝 测试凭证："
echo "   管理员: test_admin / admin123"
echo "   普通用户: test_user / password123"
echo ""
echo "🔑 环境变量已设置，现在可以运行测试："
echo "   export \$(cat .env.test | grep -v '^#' | xargs)"
echo "   pytest tests/"
echo ""
echo -e "${GREEN}✨ 测试数据库已隔离，不会影响开发数据！${NC}"
