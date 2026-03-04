"""数据库配置和连接管理"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库连接字符串
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/ai_teacher_platform?charset=utf8mb4"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # 连接前检查连接是否有效
    pool_recycle=3600,      # 连接回收时间（秒）
    pool_size=20,           # 连接池大小（默认5）
    max_overflow=40,        # 最大溢出连接数（默认10）
    pool_timeout=30,        # 获取连接超时时间（秒）
    echo=False              # 是否打印SQL语句（开发时可设为True）
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，用于定义数据模型
Base = declarative_base()


def get_db():
    """获取数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

