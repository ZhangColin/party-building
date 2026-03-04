# -*- coding: utf-8 -*-
"""
pytest 配置文件：自动加载测试环境变量

这个文件会在 pytest 运行时首先被执行，用于加载测试专用的环境变量
"""
import os
from pathlib import Path

# 获取 backend 目录
backend_dir = Path(__file__).parent

# 加载测试环境变量
env_test_file = backend_dir / ".env.test"
if env_test_file.exists():
    # 读取 .env.test 文件并设置环境变量
    with open(env_test_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
else:
    # 如果 .env.test 不存在，设置测试数据库的默认值
    os.environ.setdefault('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/ai_teacher_platform_test?charset=utf8mb4')
    os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing-only')
