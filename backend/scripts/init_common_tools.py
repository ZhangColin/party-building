"""初始化常用工具数据"""
import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from datetime import datetime
from sqlalchemy.orm import Session

# 导入数据库相关模块
import database
from database import Base, engine
import db_models
from db_models import ToolCategoryModel, CommonToolModel, CommonToolType


def init_common_tools_data(db: Session):
    """初始化常用工具数据"""
    print("开始初始化常用工具数据...")
    
    # 检查是否已有数据
    existing_categories = db.query(ToolCategoryModel).count()
    if existing_categories > 0:
        print(f"数据库中已有 {existing_categories} 个分类，跳过初始化")
        return
    
    try:
        # 创建分类
        categories = [
            ToolCategoryModel(
                id="doc-tools",
                name="文档工具",
                icon="document-text",
                order=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ToolCategoryModel(
                id="data-tools",
                name="数据工具",
                icon="chart-bar",
                order=2,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        for category in categories:
            db.add(category)
        
        print(f"已创建 {len(categories)} 个分类")
        
        # 创建工具
        tools = [
            CommonToolModel(
                id="markdown-editor",
                name="Markdown编辑器",
                description="在线编辑Markdown文档，实时预览，支持导出Word/PDF",
                category_id="doc-tools",
                type=CommonToolType.built_in,
                icon="document-text",
                html_path=None,
                order=1,
                visible=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            # 预留一个HTML工具示例（可选，后续由用户添加HTML文件）
            # CommonToolModel(
            #     id="json-formatter",
            #     name="JSON格式化工具",
            #     description="格式化和验证JSON字符串，语法高亮显示",
            #     category_id="data-tools",
            #     type=CommonToolType.html,
            #     icon="code-bracket",
            #     html_path="common_tools/html/json-formatter/index.html",
            #     order=2,
            #     visible=True,
            #     created_at=datetime.now(),
            #     updated_at=datetime.now()
            # )
        ]
        
        for tool in tools:
            db.add(tool)
        
        print(f"已创建 {len(tools)} 个工具")
        
        # 提交事务
        db.commit()
        print("常用工具数据初始化完成！")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败：{e}")
        raise


def main():
    """主函数"""
    print("=" * 50)
    print("初始化常用工具数据脚本")
    print("=" * 50)
    
    # 创建所有表（如果不存在）
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    
    # 创建数据库会话
    db = Session(engine)
    
    try:
        init_common_tools_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
