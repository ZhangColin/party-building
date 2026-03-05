# -*- coding: utf-8 -*-
"""知识库服务 - RAG检索增强生成"""
import os
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# 全局知识库实例
_kb_instance = None


class KnowledgeBaseService:
    """知识库服务 - 基于LangChain + FAISS的RAG实现"""
    
    def __init__(self, knowledge_dir: str = None):
        """
        初始化知识库服务
        
        Args:
            knowledge_dir: 知识库目录路径
        """
        if knowledge_dir is None:
            # 默认知识库目录
            project_root = Path(__file__).parent.parent.parent.parent
            knowledge_dir = project_root / "static" / "knowledge_base"
        
        self.knowledge_dir = Path(knowledge_dir)
        self.vectorstore = None
        self.embeddings = None
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """检查知识库是否已初始化"""
        return self._initialized and self.vectorstore is not None
    
    async def initialize(self) -> None:
        """
        初始化知识库：加载文档、分片、向量化
        
        此方法会：
        1. 加载知识库目录中的所有Markdown文档
        2. 将文档分片（chunk_size=500, overlap=50）
        3. 使用中文向量模型进行向量化
        4. 创建FAISS向量索引
        """
        global _kb_instance
        
        if self._initialized:
            logger.info("知识库已初始化，跳过")
            return
        
        try:
            # 延迟导入，避免启动时报错
            from langchain_community.document_loaders import DirectoryLoader
            from langchain_community.document_loaders import UnstructuredMarkdownLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            logger.info(f"开始初始化知识库，目录: {self.knowledge_dir}")
            
            # 检查目录是否存在
            if not self.knowledge_dir.exists():
                logger.warning(f"知识库目录不存在: {self.knowledge_dir}")
                self._initialized = False
                return
            
            # 1. 加载文档
            logger.info("加载Markdown文档...")
            loader = DirectoryLoader(
                str(self.knowledge_dir),
                glob="**/*.md",
                loader_cls=UnstructuredMarkdownLoader
            )
            documents = loader.load()
            logger.info(f"加载了 {len(documents)} 个文档")
            
            if not documents:
                logger.warning("没有找到任何文档")
                self._initialized = False
                return
            
            # 2. 文档分片
            logger.info("文档分片...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
            )
            splits = text_splitter.split_documents(documents)
            logger.info(f"分片后得到 {len(splits)} 个文本片段")
            
            # 3. 初始化向量模型（使用中文模型）
            logger.info("初始化向量模型...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="shibing624/text2vec-base-chinese",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # 4. 创建向量存储
            logger.info("创建向量索引...")
            self.vectorstore = FAISS.from_documents(splits, self.embeddings)
            
            self._initialized = True
            _kb_instance = self
            logger.info("知识库初始化完成")
            
        except ImportError as e:
            logger.error(f"缺少依赖库: {e}")
            logger.error("请安装: pip install langchain langchain-community faiss-cpu sentence-transformers")
            self._initialized = False
            raise
        except Exception as e:
            logger.error(f"知识库初始化失败: {e}")
            self._initialized = False
            raise
    
    def search(self, query: str, top_k: int = 3) -> List:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回的最相关文档数量
            
        Returns:
            List[Document]: 最相关的文档列表
        """
        if not self._initialized or not self.vectorstore:
            raise RuntimeError("知识库未初始化，请先调用 initialize()")
        
        try:
            results = self.vectorstore.similarity_search(query, k=top_k)
            return results
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []


def get_knowledge_base_service() -> KnowledgeBaseService:
    """获取知识库服务实例"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBaseService()
    return _kb_instance
