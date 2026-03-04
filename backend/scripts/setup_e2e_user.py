#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建E2E测试用户

用于为Playwright E2E测试创建测试账号
"""
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from src.db_models import UserModel

# 数据库配置（从.env读取）
from dotenv import load_dotenv
load_dotenv('.env')

def create_e2e_test_user():
    """创建E2E测试用户"""
    # 获取数据库URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ 错误：DATABASE_URL 环境变量未设置")
        return False

    print(f"📡 连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")

    # 创建数据库连接
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    try:
        session = SessionLocal()

        # 检查用户是否已存在
        existing_user = session.query(UserModel).filter(
            UserModel.email == 'e2etest@example.com'
        ).first()

        if existing_user:
            print("✅ E2E测试用户已存在")
            print(f"   邮箱: e2etest@example.com")
            print(f"   密码: Test123456!")
            return True

        # 创建新用户
        password = 'Test123456!'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = UserModel(
            username='e2etest',
            email='e2etest@example.com',
            password_hash=hashed_password,
            is_admin=False
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print("✅ E2E测试用户创建成功")
        print(f"   用户ID: {user.user_id}")
        print(f"   用户名: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   密码: Test123456!")

        return True

    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='创建E2E测试用户')
    parser.add_argument('--force', action='store_true', help='强制重新创建用户（如果已存在）')

    args = parser.parse_args()

    if args.force:
        print("⚠️  --force 选项暂未实现")
        print("   如需重新创建，请手动删除数据库中的用户")

    success = create_e2e_test_user()
    sys.exit(0 if success else 1)
