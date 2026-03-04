#!/usr/bin/env python3
"""
开发数据库初始化脚本
"""
import pymysql
import sys

def main():
    print("🔧 开始初始化开发数据库...")

    # 数据库配置
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'truth',
        'charset': 'utf8mb4'
    }
    db_name = 'hcy_studio'

    try:
        # 连接 MySQL 服务器
        print(f"📡 连接到 MySQL 服务器...")
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        # 检查并删除数据库（如果存在）
        cursor.execute(f"SHOW DATABASES LIKE %s", (db_name,))
        if cursor.fetchone():
            print(f"⚠️  数据库 '{db_name}' 已存在")
            response = input("是否删除并重新创建？这将清空所有数据！(y/N): ")
            if response.lower() == 'y':
                cursor.execute(f"DROP DATABASE {db_name}")
                print(f"🗑️  已删除数据库 '{db_name}'")
            else:
                print("❌ 取消操作")
                conn.close()
                sys.exit(0)

        # 创建数据库
        print(f"🗄️  创建数据库 '{db_name}'...")
        cursor.execute(
            f"CREATE DATABASE {db_name} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"✅ 数据库 '{db_name}' 创建成功")

        conn.close()

        # 连接到新创建的数据库
        conn = pymysql.connect(database=db_name, **config)
        cursor = conn.cursor()

        # 导入并运行 Alembic 迁移
        print("📋 运行数据库迁移...")

        # 使用 Alembic API 运行迁移
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        # 设置数据库 URL
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{db_name}?charset=utf8mb4"
        )

        # 运行迁移
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库迁移完成")

        # 检查创建的表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 已创建 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table[0]}")

        # 检查初始管理员用户
        cursor.execute("SELECT username, email, is_admin FROM users WHERE username = %s", ("colin",))
        admin_user = cursor.fetchone()

        if admin_user:
            print(f"\n👤 初始管理员用户已创建:")
            print(f"   用户名: {admin_user[0]}")
            print(f"   邮箱: {admin_user[1]}")
            print(f"   密码: Hcy@2026")
            print(f"   管理员: {'是' if admin_user[2] else '否'}")
        else:
            print("\n⚠️  未找到管理员用户，请检查迁移文件")

        conn.close()

        print(f"\n🎉 开发数据库初始化完成！")
        print(f"\n📝 数据库信息:")
        print(f"   数据库名: {db_name}")
        print(f"   主机: {config['host']}:{config['port']}")
        print(f"\n🚀 现在可以启动后端服务:")
        print(f"   cd backend")
        print(f"   python -m src.main")

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
