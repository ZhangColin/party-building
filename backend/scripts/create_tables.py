"""创建数据库表的脚本"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import engine, Base
from src.db_models import UserModel, SessionModel, MessageModel, ArtifactModel

def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("\n已创建的表：")
    print("- users")
    print("- sessions")
    print("- messages")
    print("- artifacts")

if __name__ == "__main__":
    create_tables()

