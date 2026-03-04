#!/usr/bin/env python3
"""
系统初始化用户创建脚本

用法：
    python scripts/create_initial_user.py

功能：
    - 创建系统初始化用户（如果不存在）
    - 创建默认管理员用户（如果不存在）
    
用户信息：
    1. 管理员用户：
        - 用户名：admin
        - 密码：HcyAdmin@2026
        - 昵称：系统管理员
        - 角色：管理员
    
    2. 普通用户（可选）：
        - 用户名：colin
        - 密码：Hcy@2026
        - 昵称：文野
        - 邮箱：zhangjinhua@aieducenter.com
        - 手机：18001828301
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uuid
import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.db_models import UserModel


def create_user_if_not_exists(db: Session, username: str, password: str, nickname: str = None, 
                                email: str = None, phone: str = None, is_admin: bool = False):
    """创建用户（如果不存在）"""
    # 检查用户是否已存在
    filters = [UserModel.username == username]
    if email:
        filters.append(UserModel.email == email)
    if phone:
        filters.append(UserModel.phone == phone)
    
    from sqlalchemy import or_
    existing_user = db.query(UserModel).filter(or_(*filters)).first()
    
    if existing_user:
        print(f"⚠️  用户已存在：{existing_user.username}")
        if is_admin and not existing_user.is_admin:
            # 更新为管理员
            existing_user.is_admin = True
            db.commit()
            print(f"   ✅ 已更新为管理员权限")
        return existing_user
    
    # 创建新用户
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_user = UserModel(
        user_id=user_id,
        username=username,
        nickname=nickname or username,
        email=email,
        phone=phone,
        password_hash=password_hash,
        avatar=None,
        is_admin=is_admin,
        created_at=datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    role = "管理员" if is_admin else "普通用户"
    print(f"✅ {role}创建成功：{new_user.username}")
    return new_user


def create_initial_user():
    """创建系统初始化用户"""
    db: Session = SessionLocal()
    try:
        print("🚀 开始创建系统初始化用户...\n")
        
        # 1. 创建管理员用户
        print("📌 创建管理员用户...")
        admin_user = create_user_if_not_exists(
            db=db,
            username="admin",
            password="HcyAdmin@2026",
            nickname="系统管理员",
            email="admin@aieducenter.com",
            phone=None,
            is_admin=True
        )
        
        if admin_user:
            print(f"   用户ID：{admin_user.user_id}")
            print(f"   用户名：{admin_user.username}")
            print(f"   昵称：{admin_user.nickname}")
            print(f"   邮箱：{admin_user.email or '未设置'}")
            print(f"   角色：管理员")
            print(f"   密码：HcyAdmin@2026")
            print()
        
        # 2. 创建普通用户（可选，如果需要）
        # print("📌 创建普通用户...")
        # colin_user = create_user_if_not_exists(
        #     db=db,
        #     username="colin",
        #     password="Hcy@2026",
        #     nickname="文野",
        #     email="zhangjinhua@aieducenter.com",
        #     phone="18001828301",
        #     is_admin=False
        # )
        
        print("\n" + "="*50)
        print("📝 登录信息：")
        print("="*50)
        print("管理员账号：")
        print("   用户名：admin")
        print("   密码：HcyAdmin@2026")
        print("   角色：管理员（拥有所有权限）")
        print()
        print("✅ 用户创建完成！")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建用户失败：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 开始创建系统初始化用户...\n")
    create_initial_user()

