# AI聊天附件功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在AI聊天中添加文件附件功能，支持本地上传和知识库/党建活动文件选择

**架构:** 最小改动方案 - 扩展 ChatInput.vue 组件，新增临时文件上传接口，扩展聊天接口支持附件参数

**Tech Stack:** Vue 3, TypeScript, FastAPI, SQLAlchemy, pytest, Vitest

**设计文档:** [docs/plans/2026-03-05-chat-attachments-design.md](./2026-03-05-chat-attachments-design.md)

---

## 前置检查

### 确保测试数据库配置

在开始实现前，确认 `backend/.env.test` 存在并指向独立的测试数据库：

```bash
# backend/.env.test
DATABASE_URL=mysql+pymysql://test_user:test_pass@localhost:3307/party_building_test
```

---

## 第一阶段：后端 - 临时文件处理

### Task 1.1: 创建临时文件目录和配置

**Files:**
- Create: `backend/src/config/temp_files.py`
- Modify: `backend/src/config_loader.py`

**Step 1: 添加临时文件配置类**

创建 `backend/src/config/temp_files.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件配置"""
import os
from pathlib import Path

class TempFileConfig:
    """临时文件配置"""
    # 临时文件目录
    TEMP_DIR = Path("uploads/temp")
    # 最大文件大小（字节）
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    # 清理间隔（小时）
    CLEANUP_INTERVAL_HOURS = 1
    # 文件最大存活时间（小时）
    MAX_AGE_HOURS = 1

    @classmethod
    def ensure_temp_dir(cls):
        """确保临时文件目录存在"""
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

# 启动时确保目录存在
TempFileConfig.ensure_temp_dir()
```

**Step 2: 在 config_loader.py 中导入配置**

在 `backend/src/config_loader.py` 末尾添加:

```python
# 导入临时文件配置，确保目录存在
from src.config.temp_files import TempFileConfig
```

**Step 3: 创建临时文件目录**

```bash
mkdir -p backend/uploads/temp
```

**Step 4: 验证目录创建**

```bash
ls -la backend/uploads/temp
```

Expected: 目录存在且为空

**Step 5: 提交**

```bash
git add backend/src/config/temp_files.py backend/src/config_loader.py
git commit -m "feat: 添加临时文件配置"
```

---

### Task 1.2: 创建临时文件模型

**Files:**
- Create: `backend/src/models/temp_files.py`

**Step 1: 创建临时文件响应模型**

创建 `backend/src/models/temp_files.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件相关模型"""
from pydantic import BaseModel

class TempFileUploadResponse(BaseModel):
    """临时文件上传响应"""
    temp_id: str
    filename: str
    size: int
    content_preview: str | None = None

class AttachmentReference(BaseModel):
    """附件引用（用于聊天请求）"""
    id: str  # 临时文件ID或文档ID
    type: str  # 'temp' | 'knowledge' | 'party'
    name: str
```

**Step 2: 在 __init__.py 中导出**

确保 `backend/src/models/__init__.py` 包含:

```python
from .temp_files import TempFileUploadResponse, AttachmentReference
```

**Step 3: 运行类型检查**

```bash
cd backend && python -c "from src.models import TempFileUploadResponse, AttachmentReference; print('Import successful')"
```

Expected: 无错误，打印 "Import successful"

**Step 4: 提交**

```bash
git add backend/src/models/temp_files.py backend/src/models/__init__.py
git commit -m "feat: 添加临时文件模型"
```

---

### Task 1.3: 创建临时文件服务

**Files:**
- Create: `backend/src/services/temp_file_service.py`

**Step 1: 编写临时文件服务测试**

创建 `backend/tests/unit/test_temp_file_service.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件服务单元测试"""
import pytest
from pathlib import Path
from src.services.temp_file_service import TempFileService
from src.config.temp_files import TempFileConfig

@pytest.fixture
def temp_service():
    """创建临时文件服务实例"""
    return TempFileService()

@pytest.fixture
def temp_dir():
    """获取临时文件目录"""
    return TempFileConfig.TEMP_DIR

def test_save_temp_file(temp_service, temp_dir):
    """测试保存临时文件"""
    content = b"test content"
    filename = "test.txt"

    response = temp_service.save_file(content, filename)

    assert response.temp_id
    assert response.filename == filename
    assert response.size == len(content)
    assert response.content_preview == "test content"

    # 验证文件存在
    file_path = temp_dir / f"{response.temp_id}.tmp"
    assert file_path.exists()

    # 清理
    temp_service.delete_file(response.temp_id)

def test_get_temp_file(temp_service, temp_dir):
    """测试获取临时文件内容"""
    content = b"test content for get"
    filename = "test_get.txt"

    save_response = temp_service.save_file(content, filename)
    retrieved_content = temp_service.get_file_content(save_response.temp_id)

    assert retrieved_content == content

    # 清理
    temp_service.delete_file(save_response.temp_id)

def test_get_nonexistent_file(temp_service):
    """测试获取不存在的文件"""
    result = temp_service.get_file_content("nonexistent-id")
    assert result is None

def test_delete_temp_file(temp_service, temp_dir):
    """测试删除临时文件"""
    content = b"test content for delete"
    filename = "test_delete.txt"

    save_response = temp_service.save_file(content, filename)
    file_path = temp_dir / f"{save_response.temp_id}.tmp"

    # 确认文件存在
    assert file_path.exists()

    # 删除文件
    result = temp_service.delete_file(save_response.temp_id)
    assert result is True

    # 确认文件不存在
    assert not file_path.exists()

def test_file_size_limit(temp_service):
    """测试文件大小限制"""
    # 创建一个超过限制的文件（11MB）
    large_content = b"x" * (11 * 1024 * 1024)
    filename = "large.txt"

    with pytest.raises(ValueError, match="文件大小超过限制"):
        temp_service.save_file(large_content, filename)

def test_cleanup_old_files(temp_service, temp_dir):
    """测试清理旧文件"""
    # 创建一些测试文件
    content = b"old content"
    filename = "old.txt"

    save_response = temp_service.save_file(content, filename)
    file_path = temp_dir / f"{save_response.temp_id}.tmp"

    # 修改文件修改时间（模拟旧文件）
    import time
    old_time = time.time() - (2 * 3600)  # 2小时前
    import os
    os.utime(file_path, (old_time, old_time))

    # 执行清理
    cleaned_count = temp_service.cleanup_old_files()

    assert cleaned_count >= 1
    assert not file_path.exists()
```

**Step 2: 运行测试（预期失败）**

```bash
cd backend && pytest tests/unit/test_temp_file_service.py -v
```

Expected: FAIL - ModuleNotFoundError: No module named 'src.services.temp_file_service'

**Step 3: 实现临时文件服务**

创建 `backend/src/services/temp_file_service.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件服务"""
import os
import time
import uuid
from pathlib import Path
from typing import Optional
from src.config.temp_files import TempFileConfig
from src.models.temp_files import TempFileUploadResponse

class TempFileService:
    """临时文件服务"""

    def __init__(self):
        self.temp_dir = TempFileConfig.TEMP_DIR
        self.max_size = TempFileConfig.MAX_FILE_SIZE
        self.max_age_seconds = TempFileConfig.MAX_AGE_HOURS * 3600

    def save_file(self, content: bytes, filename: str) -> TempFileUploadResponse:
        """
        保存临时文件

        Args:
            content: 文件内容
            filename: 原始文件名

        Returns:
            TempFileUploadResponse

        Raises:
            ValueError: 文件大小超过限制
        """
        # 检查文件大小
        if len(content) > self.max_size:
            raise ValueError(
                f"文件大小超过限制（最大 {self.max_size // (1024 * 1024)}MB）"
            )

        # 生成唯一ID
        temp_id = str(uuid.uuid4())

        # 保存文件
        file_path = self.temp_dir / f"{temp_id}.tmp"
        with open(file_path, 'wb') as f:
            f.write(content)

        # 生成内容预览（前1000字符）
        content_preview = None
        try:
            text_content = content.decode('utf-8', errors='ignore')
            content_preview = text_content[:1000]
        except Exception:
            pass

        return TempFileUploadResponse(
            temp_id=temp_id,
            filename=filename,
            size=len(content),
            content_preview=content_preview
        )

    def get_file_content(self, temp_id: str) -> Optional[bytes]:
        """
        获取临时文件内容

        Args:
            temp_id: 临时文件ID

        Returns:
            文件内容，不存在返回 None
        """
        file_path = self.temp_dir / f"{temp_id}.tmp"
        if not file_path.exists():
            return None

        with open(file_path, 'rb') as f:
            return f.read()

    def delete_file(self, temp_id: str) -> bool:
        """
        删除临时文件

        Args:
            temp_id: 临时文件ID

        Returns:
            是否删除成功
        """
        file_path = self.temp_dir / f"{temp_id}.tmp"
        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except Exception:
            return False

    def cleanup_old_files(self) -> int:
        """
        清理过期的临时文件

        Returns:
            清理的文件数量
        """
        current_time = time.time()
        cleaned_count = 0

        for file_path in self.temp_dir.glob("*.tmp"):
            # 检查文件修改时间
            file_mtime = file_path.stat().st_mtime
            age_seconds = current_time - file_mtime

            if age_seconds > self.max_age_seconds:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception:
                    pass

        return cleaned_count
```

**Step 4: 运行测试（预期通过）**

```bash
cd backend && pytest tests/unit/test_temp_file_service.py -v
```

Expected: PASS - 所有测试通过

**Step 5: 提交**

```bash
git add backend/tests/unit/test_temp_file_service.py backend/src/services/temp_file_service.py
git commit -m "feat: 添加临时文件服务及单元测试"
```

---

### Task 1.4: 创建临时文件上传接口

**Files:**
- Create: `backend/src/interfaces/routers/temp_files/router.py`
- Create: `backend/src/interfaces/routers/temp_files/__init__.py`
- Modify: `backend/src/main.py`

**Step 1: 编写接口测试**

创建 `backend/tests/integration/test_temp_files_api.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件API集成测试"""
import pytest
import io
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_temp_file_success():
    """测试成功上传临时文件"""
    # 创建测试文件
    file_content = b"test file content for upload"
    file_data = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/temp-files/upload",
        files={"file": ("test.txt", file_data, "text/plain")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["temp_id"]
    assert data["filename"] == "test.txt"
    assert data["size"] == len(file_content)
    assert data["content_preview"] == "test file content for upload"

def test_upload_file_too_large():
    """测试上传超大文件"""
    # 创建超过限制的文件（11MB）
    large_content = b"x" * (11 * 1024 * 1024)
    file_data = io.BytesIO(large_content)

    response = client.post(
        "/api/v1/temp-files/upload",
        files={"file": ("large.txt", file_data, "text/plain")}
    )

    assert response.status_code == 400
    assert "文件大小超过限制" in response.json()["detail"]

def test_upload_file_no_file():
    """测试没有文件的上传"""
    response = client.post("/api/v1/temp-files/upload")

    assert response.status_code == 422  # Validation error
```

**Step 2: 运行测试（预期失败）**

```bash
cd backend && pytest tests/integration/test_temp_files_api.py -v
```

Expected: FAIL - 404 Not Found

**Step 3: 创建临时文件路由**

创建 `backend/src/interfaces/routers/temp_files/router.py`:

```python
# -*- coding: utf-8 -*-
"""临时文件路由"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.temp_file_service import TempFileService
from src.models.temp_files import TempFileUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=TempFileUploadResponse, tags=["临时文件"])
async def upload_temp_file(
    file: UploadFile = File(...),
    temp_file_service: TempFileService = TempFileService
):
    """
    上传临时文件

    用于聊天时从本地上传的文件，消息发送后自动清理
    """
    try:
        # 读取文件内容
        content = await file.read()

        # 保存临时文件
        response = temp_file_service.save_file(content, file.filename)

        logger.info(f"临时文件上传成功: {response.temp_id}, 文件名: {response.filename}")
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"临时文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")
```

创建 `backend/src/interfaces/routers/temp_files/__init__.py`:

```python
# -*- coding: utf-8 -*-
from .router import router
```

**Step 4: 在 main.py 中注册路由**

在 `backend/src/main.py` 的路由注册部分添加:

```python
from src.interfaces.routers.temp_files import router as temp_files_router

# 注册临时文件路由
app.include_router(temp_files_router, prefix="/api/v1/temp-files", tags=["临时文件"])
```

**Step 5: 运行测试（预期通过）**

```bash
cd backend && pytest tests/integration/test_temp_files_api.py -v
```

Expected: PASS - 所有测试通过

**Step 6: 提交**

```bash
git add backend/src/interfaces/routers/temp_files/ backend/src/main.py backend/tests/integration/test_temp_files_api.py
git commit -m "feat: 添加临时文件上传API"
```

---

### Task 1.5: 扩展聊天请求模型

**Files:**
- Modify: `backend/src/models.py`

**Step 1: 查看现有 ChatRequest 模型**

```bash
grep -A 10 "class ChatRequest" backend/src/models.py
```

**Step 2: 扩展 ChatRequest 模型**

在 `backend/src/models.py` 中找到 `ChatRequest` 类，添加 `attached_files` 字段:

```python
class ChatRequest(BaseModel):
    """对话请求"""
    message: str  # 用户输入的消息
    session_id: str | None = None  # 会话 UUID（可选）
    history: list[Message] | None = None  # 历史消息列表（可选）
    attached_files: list[AttachmentReference] | None = None  # 新增：附件列表
```

确保在同一文件中导入 `AttachmentReference`:

```python
from .models.temp_files import AttachmentReference
```

**Step 3: 运行类型检查**

```bash
cd backend && python -c "from src.models import ChatRequest; print('Import successful')"
```

Expected: 无错误

**Step 4: 提交**

```bash
git add backend/src/models.py
git commit -m "feat: 扩展ChatRequest支持附件"
```

---

### Task 1.6: 创建批量获取文档内容接口（知识库）

**Files:**
- Modify: `backend/src/interfaces/routers/knowledge/router.py`
- Create: `backend/tests/integration/test_knowledge_batch_api.py`

**Step 1: 编写批量获取测试**

创建 `backend/tests/integration/test_knowledge_batch_api.py`:

```python
# -*- coding: utf-8 -*-
"""知识库批量获取API测试"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_batch_get_documents_empty_list():
    """测试空列表批量获取"""
    response = client.post(
        "/api/v1/knowledge/documents/batch",
        json={"document_ids": []}
    )

    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert data["documents"] == []

def test_batch_get_documents_success():
    """测试批量获取文档（需要先有测试数据）"""
    # 注意：此测试需要数据库中有测试文档
    # 或者使用 mock
    response = client.post(
        "/api/v1/knowledge/documents/batch",
        json={"document_ids": ["test-doc-1", "test-doc-2"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
```

**Step 2: 运行测试（预期失败）**

```bash
cd backend && pytest tests/integration/test_knowledge_batch_api.py -v
```

Expected: FAIL - 404 Not Found

**Step 3: 在知识库路由中添加批量获取接口**

在 `backend/src/interfaces/routers/knowledge/router.py` 中添加:

```python
@router.post("/documents/batch", tags=["知识库"])
async def batch_get_documents(
    request: BatchDocumentRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    批量获取文档内容

    用于聊天时从知识库选择文件
    """
    try:
        documents = knowledge_service.batch_get_documents(request.document_ids)
        return {"documents": documents}
    except Exception as e:
        logger.error(f"批量获取文档失败: {e}")
        raise HTTPException(status_code=500, detail="获取文档内容失败")
```

同时在文件顶部添加请求模型:

```python
class BatchDocumentRequest(BaseModel):
    """批量获取文档请求"""
    document_ids: list[str]
```

**Step 4: 在知识库服务中添加批量获取方法**

在 `backend/src/services/knowledge_service.py` 中的 `KnowledgeService` 类添加:

```python
def batch_get_documents(self, document_ids: list[str]) -> list[dict]:
    """
    批量获取文档内容

    Args:
        document_ids: 文档ID列表

    Returns:
        文档内容列表
    """
    from src.db_models import KnowledgeDocumentModel

    documents = []
    for doc_id in document_ids:
        doc = self.db.query(KnowledgeDocumentModel).filter(
            KnowledgeDocumentModel.id == doc_id
        ).first()

        if doc and doc.markdown_path:
            try:
                with open(doc.markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                documents.append({
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "content": content
                })
            except Exception as e:
                logger.warning(f"读取文档 {doc_id} 内容失败: {e}")

    return documents
```

**Step 5: 运行测试**

```bash
cd backend && pytest tests/integration/test_knowledge_batch_api.py -v
```

Expected: PASS

**Step 6: 提交**

```bash
git add backend/src/interfaces/routers/knowledge/router.py backend/src/services/knowledge_service.py backend/tests/integration/test_knowledge_batch_api.py
git commit -m "feat: 添加知识库批量获取文档接口"
```

---

### Task 1.7: 创建批量获取文档内容接口（党建活动）

**Files:**
- Modify: `backend/src/interfaces/routers/party/router.py`
- Create: `backend/tests/integration/test_party_batch_api.py`

**Step 1: 编写批量获取测试**

创建 `backend/tests/integration/test_party_batch_api.py`:

```python
# -*- coding: utf-8 -*-
"""党建活动批量获取API测试"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_batch_get_party_documents_empty_list():
    """测试空列表批量获取"""
    response = client.post(
        "/api/v1/party-activities/documents/batch",
        json={"document_ids": []}
    )

    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert data["documents"] == []
```

**Step 2: 运行测试（预期失败）**

```bash
cd backend && pytest tests/integration/test_party_batch_api.py -v
```

Expected: FAIL - 404 Not Found

**Step 3: 在党建活动路由中添加批量获取接口**

在 `backend/src/interfaces/routers/party/router.py` 中添加（类似于知识库）:

```python
@router.post("/documents/batch", tags=["党建活动"])
async def batch_get_party_documents(
    request: BatchDocumentRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
):
    """
    批量获取党建活动文档内容

    用于聊天时从党建活动选择文件
    """
    try:
        from src.services.organization_life_service import OrganizationLifeService
        service = OrganizationLifeService()
        documents = service.batch_get_documents(request.document_ids)
        return {"documents": documents}
    except Exception as e:
        logger.error(f"批量获取党建文档失败: {e}")
        raise HTTPException(status_code=500, detail="获取文档内容失败")
```

**Step 4: 在党建活动服务中添加批量获取方法**

在 `backend/src/services/organization_life_service.py` 中添加:

```python
def batch_get_documents(self, document_ids: list[str]) -> list[dict]:
    """
    批量获取文档内容

    Args:
        document_ids: 文档ID列表

    Returns:
        文档内容列表
    """
    from src.db_models_party import PartyActivityDocumentModel

    documents = []
    for doc_id in document_ids:
        doc = self.db.query(PartyActivityDocumentModel).filter(
            PartyActivityDocumentModel.id == doc_id
        ).first()

        if doc and doc.markdown_path:
            try:
                with open(doc.markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                documents.append({
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "content": content
                })
            except Exception as e:
                logger.warning(f"读取党建文档 {doc_id} 内容失败: {e}")

    return documents
```

**Step 5: 运行测试**

```bash
cd backend && pytest tests/integration/test_party_batch_api.py -v
```

Expected: PASS

**Step 6: 提交**

```bash
git add backend/src/interfaces/routers/party/router.py backend/src/services/organization_life_service.py backend/tests/integration/test_party_batch_api.py
git commit -m "feat: 添加党建活动批量获取文档接口"
```

---

### Task 1.8: 扩展聊天接口支持附件

**Files:**
- Modify: `backend/src/interfaces/routers/tools/chat.py`
- Modify: `backend/src/services/ai_service.py`
- Create: `backend/tests/integration/test_chat_with_attachments.py`

**Step 1: 编写带附件的聊天测试**

创建 `backend/tests/integration/test_chat_with_attachments.py`:

```python
# -*- coding: utf-8 -*-
"""带附件的聊天集成测试"""
import pytest
import io
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# 测试用户token（需要在测试环境中创建）
TEST_TOKEN = "test-token"

def test_chat_with_temp_file_attachment():
    """测试带临时文件附件的聊天"""
    # 先上传临时文件
    file_content = b"这是一份测试文档的内容，用于AI聊天。"
    file_data = io.BytesIO(file_content)

    upload_response = client.post(
        "/api/v1/temp-files/upload",
        files={"file": ("test.txt", file_data, "text/plain")}
    )
    assert upload_response.status_code == 200
    temp_id = upload_response.json()["temp_id"]

    # 发送带附件的聊天消息
    chat_response = client.post(
        "/api/v1/tools/test-tool/chat/stream",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "message": "请总结附件内容",
            "attached_files": [
                {
                    "id": temp_id,
                    "type": "temp",
                    "name": "test.txt"
                }
            ]
        }
    )

    assert chat_response.status_code == 200

def test_chat_with_knowledge_attachment():
    """测试带知识库附件的聊天"""
    chat_response = client.post(
        "/api/v1/tools/test-tool/chat/stream",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "message": "请分析文档内容",
            "attached_files": [
                {
                    "id": "knowledge-doc-1",
                    "type": "knowledge",
                    "name": "文档.md"
                }
            ]
        }
    )

    # 可能404因为工具不存在，但请求格式应该正确
    assert chat_response.status_code in [200, 404, 401]
```

**Step 2: 运行测试（预期部分失败）**

```bash
cd backend && pytest tests/integration/test_chat_with_attachments.py -v
```

Expected: 部分测试可能因为认证失败

**Step 3: 扩展 AI 服务支持附件注入**

在 `backend/src/services/ai_service.py` 的 `AIService` 类中添加方法:

```python
def build_system_prompt_with_attachments(
    self,
    base_system_prompt: str,
    attachments: list[dict]
) -> str:
    """
    构建包含附件内容的 system_prompt

    Args:
        base_system_prompt: 基础系统提示词
        attachments: 附件列表，每个包含 name 和 content

    Returns:
        构建后的系统提示词
    """
    if not attachments:
        return base_system_prompt

    # 构建附件内容部分
    attachment_content = "用户附件内容：\n"

    for i, att in enumerate(attachments, 1):
        name = att.get("name", f"文件{i}")
        content = att.get("content", "")

        # 截断过长内容
        if len(content) > 10000:
            content = content[:10000] + "\n（因内容过长，后续内容已省略）"

        attachment_content += f"\n【文件{i}：{name}】\n{content}\n"

    # 组合最终 prompt
    return f"{base_system_prompt}\n\n---\n{attachment_content}\n---\n"
```

**Step 4: 修改聊天接口处理附件**

在 `backend/src/interfaces/routers/tools/chat.py` 的 `chat_stream` 函数中添加附件处理:

```python
@router.post("/tools/{tool_id}/chat/stream", tags=["对话"])
async def chat_stream(
    tool_id: str,
    request: ChatRequest,
    # ... 现有参数
):
    # ... 现有代码

    # 新增：处理附件
    attachment_contents = []
    if request.attached_files:
        temp_file_service = TempFileService()

        for att in request.attached_files:
            content = None

            if att.type == "temp":
                # 从临时文件获取
                content_bytes = temp_file_service.get_file_content(att.id)
                if content_bytes:
                    content = content_bytes.decode('utf-8', errors='ignore')

            elif att.type == "knowledge":
                # 从知识库获取（需要调用知识库服务）
                from src.services.knowledge_service import KnowledgeService
                knowledge_service = KnowledgeService()
                docs = knowledge_service.batch_get_documents([att.id])
                if docs:
                    content = docs[0].get("content")

            elif att.type == "party":
                # 从党建活动获取
                from src.services.organization_life_service import OrganizationLifeService
                party_service = OrganizationLifeService()
                docs = party_service.batch_get_documents([att.id])
                if docs:
                    content = docs[0].get("content")

            if content:
                attachment_contents.append({
                    "name": att.name,
                    "content": content
                })

    # 构建带附件的 system_prompt
    if attachment_contents:
        system_prompt = ai_service.build_system_prompt_with_attachments(
            tool.system_prompt,
            attachment_contents
        )
    else:
        system_prompt = tool.system_prompt

    # ... 后续代码使用 system_prompt
```

**Step 5: 运行测试**

```bash
cd backend && pytest tests/integration/test_chat_with_attachments.py -v
```

**Step 6: 提交**

```bash
git add backend/src/interfaces/routers/tools/chat.py backend/src/services/ai_service.py backend/tests/integration/test_chat_with_attachments.py
git commit -m "feat: 扩展聊天接口支持附件"
```

---

## 第二阶段：前端基础

### Task 2.1: 扩展前端类型定义

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: 添加附件相关类型**

在 `frontend/src/types/index.ts` 末尾添加:

```typescript
// ==================== 聊天附件模块 ====================

/**
 * 附件文件状态
 */
export type AttachmentStatus = 'uploading' | 'ready' | 'error'

/**
 * 附件引用（用于发送给后端）
 */
export interface AttachmentReference {
  id: string  // 临时文件ID或文档ID
  type: 'temp' | 'knowledge' | 'party'
  name: string
}

/**
 * 聊天附件（前端状态）
 */
export interface ChatAttachment {
  id: string
  name: string
  type: 'temp' | 'knowledge' | 'party'
  size: number  // 文件大小（字节）
  status: AttachmentStatus
  error?: string  // 错误信息
}

/**
 * 消息附件（展示用）
 */
export interface MessageAttachment {
  id: string
  name: string
  type: 'temp' | 'knowledge' | 'party'
  size: number
}
```

**Step 2: 扩展 Message 接口**

找到 `Message` 接口并添加 `attachments` 字段:

```typescript
export interface Message {
  // ... 现有字段
  attachments?: MessageAttachment[]  // 新增：消息附件
}
```

**Step 3: 扩展 ChatRequest 接口**

找到 `ChatRequest` 接口并添加 `attached_files` 字段:

```typescript
export interface ChatRequest {
  message: string
  session_id?: string | null
  history?: Message[]
  attached_files?: AttachmentReference[]  // 新增
}
```

**Step 4: 运行类型检查**

```bash
cd frontend && npm run type-check
```

Expected: 无类型错误

**Step 5: 提交**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: 扩展前端类型定义支持附件"
```

---

### Task 2.2: 创建临时文件上传 API

**Files:**
- Create: `frontend/src/services/tempFilesApi.ts`

**Step 1: 创建临时文件 API 服务**

创建 `frontend/src/services/tempFilesApi.ts`:

```typescript
/**
 * 临时文件 API
 */
import axios from 'axios'
import type { TempFileUploadResponse } from '@/types'

const API_BASE = '/api/v1/temp-files'

/**
 * 上传临时文件
 */
export async function uploadTempFile(
  file: File,
  onProgress?: (progress: number) => void
): Promise<TempFileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post<TempFileUploadResponse>(
    `${API_BASE}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(progress)
        }
      }
    }
  )

  return response.data
}
```

**Step 2: 在 types/index.ts 中添加响应类型**

在 `frontend/src/types/index.ts` 中添加:

```typescript
/**
 * 临时文件上传响应
 */
export interface TempFileUploadResponse {
  temp_id: string
  filename: string
  size: number
  content_preview?: string
}
```

**Step 3: 提交**

```bash
git add frontend/src/services/tempFilesApi.ts frontend/src/types/index.ts
git commit -m "feat: 添加临时文件上传API服务"
```

---

### Task 2.3: 扩展 ChatInput 组件 - 基础结构

**Files:**
- Modify: `frontend/src/components/ChatInput.vue`

**Step 1: 编写 ChatInput 扩展测试**

创建 `frontend/tests/unit/ChatInput.spec.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatInput from '@/components/ChatInput.vue'

describe('ChatInput - 附件功能', () => {
  it('应该渲染文件操作按钮', () => {
    const wrapper = mount(ChatInput)
    expect(wrapper.find('[data-test="upload-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="knowledge-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="party-btn"]').exists()).toBe(true)
  })

  it('应该限制最多5个文件', async () => {
    const wrapper = mount(ChatInput, {
      props: { maxFiles: 5 }
    })

    // 模拟添加6个文件
    for (let i = 0; i < 6; i++) {
      await wrapper.vm.addAttachment({
        id: `file-${i}`,
        name: `file${i}.txt`,
        type: 'temp' as const,
        size: 1000,
        status: 'ready' as const
      })
    }

    expect(wrapper.vm.attachments.length).toBe(5)
  })

  it('应该限制单个文件最大10MB', async () => {
    const wrapper = mount(ChatInput, {
      props: { maxFileSize: 10 * 1024 * 1024 }
    })

    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.txt')
    const result = await wrapper.vm.validateFileSize(largeFile)

    expect(result.valid).toBe(false)
    expect(result.error).toContain('超过10MB')
  })
})
```

**Step 2: 运行测试（预期失败）**

```bash
cd frontend && npm run test -- ChatInput.spec.ts
```

Expected: FAIL - 新功能未实现

**Step 3: 扩展 ChatInput.vue 组件**

在 `frontend/src/components/ChatInput.vue` 中添加附件功能：

```vue
<template>
  <div class="chat-input">
    <!-- 新增：文件操作按钮区 -->
    <div v-if="showFileButtons" class="file-actions">
      <button
        data-test="upload-btn"
        class="file-btn"
        :disabled="isAtMaxFiles"
        @click="handleUploadLocal"
        title="上传本地文件"
      >
        <CloudArrowUpIcon class="w-5 h-5" />
        <span>本地文件</span>
      </button>
      <button
        data-test="knowledge-btn"
        class="file-btn"
        :disabled="isAtMaxFiles"
        @click="handleSelectKnowledge"
        title="从知识库选择"
      >
        <BuildingLibraryIcon class="w-5 h-5" />
        <span>知识库</span>
      </button>
      <button
        data-test="party-btn"
        class="file-btn"
        :disabled="isAtMaxFiles"
        @click="handleSelectParty"
        title="从党建活动选择"
      >
        <DocumentTextIcon class="w-5 h-5" />
        <span>党建活动</span>
      </button>
    </div>

    <!-- 新增：附件展示区 -->
    <div v-if="attachments.length > 0" class="attachments-area">
      <div
        v-for="att in attachments"
        :key="att.id"
        class="attachment-tag"
        :class="{ 'error': att.status === 'error' }"
      >
        <DocumentIcon class="w-4 h-4 attachment-icon" />
        <span class="attachment-name">{{ att.name }}</span>
        <span class="attachment-size">{{ formatSize(att.size) }}</span>
        <button
          class="attachment-remove"
          @click="removeAttachment(att.id)"
          title="删除"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 原有输入框和发送按钮 -->
    <textarea
      ref="textareaRef"
      v-model="inputText"
      class="input-textarea"
      :placeholder="placeholder || '输入消息...'"
      :disabled="disabled"
      rows="1"
      @keydown="handleKeyDown"
      @input="handleInput"
    ></textarea>
    <button
      class="send-button"
      :disabled="!canSend"
      @click="handleSend"
    >
      发送
    </button>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="handleFileSelected"
    >
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CloudArrowUpIcon,
  BuildingLibraryIcon,
  DocumentTextIcon,
  DocumentIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import type { ChatAttachment } from '@/types'
import { uploadTempFile } from '@/services/tempFilesApi'

const props = withDefaults(
  defineProps<{
    placeholder?: string
    disabled?: boolean
    maxFiles?: number
    maxFileSize?: number
    showFileButtons?: boolean
  }>(),
  {
    maxFiles: 5,
    maxFileSize: 10 * 1024 * 1024, // 10MB
    showFileButtons: true
  }
)

const emit = defineEmits<{
  send: [content: string, attachments: ChatAttachment[]]
}>()

// 状态
const inputText = ref('')
const attachments = ref<ChatAttachment[]>([])
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// 计算属性
const isAtMaxFiles = computed(() => attachments.value.length >= props.maxFiles)
const canSend = computed(() => inputText.value.trim() && !attachments.value.some(a => a.status === 'uploading'))

// 方法
function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function handleUploadLocal() {
  fileInputRef.value?.click()
}

async function handleFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 验证文件大小
  if (file.size > props.maxFileSize) {
    ElMessage.error(`文件大小超过限制（最大${formatSize(props.maxFileSize)}）`)
    return
  }

  // 添加到附件列表（上传中状态）
  const tempAttachment: ChatAttachment = {
    id: `temp-${Date.now()}`,
    name: file.name,
    type: 'temp',
    size: file.size,
    status: 'uploading'
  }
  attachments.value.push(tempAttachment)

  try {
    const response = await uploadTempFile(file, (progress) => {
      // 可以添加进度条
    })

    // 更新为就绪状态
    const index = attachments.value.findIndex(a => a.id === tempAttachment.id)
    if (index !== -1) {
      attachments.value[index] = {
        ...response,
        id: response.temp_id,
        type: 'temp',
        status: 'ready'
      }
    }
  } catch (error: any) {
    const index = attachments.value.findIndex(a => a.id === tempAttachment.id)
    if (index !== -1) {
      attachments.value[index].status = 'error'
      attachments.value[index].error = error.message || '上传失败'
    }
    ElMessage.error('文件上传失败')
  }

  // 清空 input
  target.value = ''
}

function removeAttachment(id: string) {
  const index = attachments.value.findIndex(a => a.id === id)
  if (index !== -1) {
    attachments.value.splice(index, 1)
  }
}

function handleSelectKnowledge() {
  // TODO: 打开知识库文件选择对话框
  ElMessage.info('知识库文件选择功能开发中')
}

function handleSelectParty() {
  // TODO: 打开党建活动文件选择对话框
  ElMessage.info('党建活动文件选择功能开发中')
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleInput() {
  // 自动调整高度
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      const scrollHeight = textareaRef.value.scrollHeight
      textareaRef.value.style.height = `${Math.min(scrollHeight, 200)}px`
    }
  })
}

function handleSend() {
  if (!canSend.value) return

  const readyAttachments = attachments.value.filter(a => a.status === 'ready')
  emit('send', inputText.value.trim(), readyAttachments)

  // 清空输入
  inputText.value = ''
  attachments.value = []
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

// 暴露方法供测试
defineExpose({
  addAttachment: (att: ChatAttachment) => {
    if (!isAtMaxFiles.value) {
      attachments.value.push(att)
    }
  },
  validateFileSize: (file: File) => {
    return {
      valid: file.size <= props.maxFileSize,
      error: file.size > props.maxFileSize
        ? `文件大小超过限制（最大${formatSize(props.maxFileSize)}）`
        : undefined
    }
  },
  attachments
})
</script>

<style scoped>
/* ... 原有样式 ... */

.file-actions {
  @apply flex items-center gap-2 mb-3;
}

.file-btn {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm transition-all;
}

.file-btn:hover:not(:disabled) {
  @apply bg-gray-50 border-gray-300;
}

.file-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.attachments-area {
  @apply flex flex-wrap gap-2 mb-3;
}

.attachment-tag {
  @apply flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm;
}

.attachment-tag.error {
  @apply bg-red-50 text-red-600;
}

.attachment-icon {
  @apply text-gray-400 flex-shrink-0;
}

.attachment-name {
  @apply truncate max-w-[150px];
}

.attachment-size {
  @apply text-gray-400 text-xs;
}

.attachment-remove {
  @apply text-gray-400 hover:text-red-500 transition-colors;
}
</style>
```

**Step 4: 运行测试**

```bash
cd frontend && npm run test -- ChatInput.spec.ts
```

**Step 5: 提交**

```bash
git add frontend/src/components/ChatInput.vue frontend/tests/unit/ChatInput.spec.ts
git commit -m "feat: 扩展ChatInput组件支持附件"
```

---

### Task 2.4: 在 ChatPanel 中展示消息附件

**Files:**
- Modify: `frontend/src/components/ChatPanel.vue`

**Step 1: 添加附件展示组件**

在 ChatPanel.vue 的消息展示区域添加附件渲染:

```vue
<template>
  <!-- ... 原有模板 ... -->
  <div
    v-for="message in messages"
    :key="message.message_id"
    class="message"
    :class="{ 'user': message.role === 'user' }"
  >
    <!-- 原有消息内容 -->
    <div class="message-content">
      {{ message.content }}
    </div>

    <!-- 新增：附件展示 -->
    <div v-if="message.attachments && message.attachments.length > 0" class="message-attachments">
      <div v-for="att in message.attachments" :key="att.id" class="message-attachment">
        <DocumentIcon class="w-4 h-4" />
        <span>{{ att.name }}</span>
        <span class="attachment-type">{{ getAttachmentTypeLabel(att.type) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ... 原有导入
import { DocumentIcon } from '@heroicons/vue/24/outline'

function getAttachmentTypeLabel(type: string): string {
  const labels = {
    'temp': '本地文件',
    'knowledge': '知识库',
    'party': '党建活动'
  }
  return labels[type] || '文件'
}
</script>

<style scoped>
.message-attachments {
  @apply mt-2 flex flex-wrap gap-2;
}

.message-attachment {
  @apply flex items-center gap-2 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600;
}
</style>
```

**Step 2: 提交**

```bash
git add frontend/src/components/ChatPanel.vue
git commit -m "feat: 在消息中展示附件"
```

---

## 第三阶段：文件选择对话框

### Task 3.1: 创建 FileSelectorDialog 组件

**Files:**
- Create: `frontend/src/components/FileSelectorDialog.vue`

**Step 1: 创建文件选择对话框组件**

创建 `frontend/src/components/FileSelectorDialog.vue`:

```vue
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="800px"
    @close="handleClose"
  >
    <div class="file-selector">
      <!-- 左侧目录树 -->
      <div class="sidebar">
        <CategoryTree
          :categories="categories"
          :current-category-id="currentCategoryId"
          :title="sidebarTitle"
          @select="handleCategorySelect"
        />
      </div>

      <!-- 右侧文件列表 -->
      <div class="main-area">
        <div class="file-list">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="file-item"
            :class="{ selected: selectedIds.has(doc.id) }"
            @click="toggleSelection(doc.id)"
          >
            <input type="checkbox" :checked="selectedIds.has(doc.id)" />
            <DocumentIcon class="w-5 h-5" />
            <span class="file-name">{{ doc.original_filename }}</span>
          </div>
        </div>
        <div v-if="documents.length === 0" class="empty-state">
          此目录暂无文件
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <span class="selection-count">已选 {{ selectedIds.size }} 项</span>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { DocumentIcon } from '@heroicons/vue/24/outline'
import CategoryTree from '@/components/file-manager/CategoryTree.vue'
import type { Category, Document } from '@/types/file-manager'

interface Props {
  modelValue: boolean
  type: 'knowledge' | 'party'
  categories: Category[]
  documents: Document[]
  sidebarTitle?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', documentIds: string[]): void
}

const props = withDefaults(defineProps<Props>(), {
  sidebarTitle: '目录'
})

const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const currentCategoryId = ref<string | null>(null)
const selectedIds = Set<string>()

const title = computed(() =>
  props.type === 'knowledge' ? '从知识库选择文件' : '从党建活动选择文件'
)

function handleCategorySelect(category: Category) {
  currentCategoryId.value = category.id
  // TODO: 加载该目录的文件
}

function toggleSelection(docId: string) {
  if (selectedIds.has(docId)) {
    selectedIds.delete(docId)
  } else {
    selectedIds.add(docId)
  }
}

function handleClose() {
  visible.value = false
  selectedIds.clear()
}

function handleConfirm() {
  emit('confirm', Array.from(selectedIds))
  handleClose()
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    selectedIds.clear()
  }
})
</script>

<style scoped>
.file-selector {
  @apply flex h-[400px];
}

.sidebar {
  @apply w-64 border-r border-gray-200 overflow-y-auto;
}

.main-area {
  @apply flex-1 overflow-y-auto p-4;
}

.file-list {
  @apply space-y-2;
}

.file-item {
  @apply flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors;
}

.file-item:hover {
  @apply bg-gray-50;
}

.file-item.selected {
  @apply bg-red-50;
}

.file-name {
  @apply flex-1 truncate;
}

.empty-state {
  @apply text-center text-gray-400 mt-10;
}

.dialog-footer {
  @apply flex items-center justify-between w-full;
}

.selection-count {
  @apply text-sm text-gray-500;
}
</style>
```

**Step 2: 提交**

```bash
git add frontend/src/components/FileSelectorDialog.vue
git commit -m "feat: 创建文件选择对话框组件"
```

---

### Task 3.2: 在 ChatInput 中集成文件选择对话框

**Files:**
- Modify: `frontend/src/components/ChatInput.vue`

**Step 1: 添加文件选择对话框**

在 ChatInput.vue 中添加:

```vue
<template>
  <!-- ... 原有内容 ... -->

  <!-- 新增：文件选择对话框 -->
  <FileSelectorDialog
    v-model="knowledgeDialogVisible"
    type="knowledge"
    :categories="knowledgeCategories"
    :documents="knowledgeDocuments"
    @confirm="handleKnowledgeSelect"
  />

  <FileSelectorDialog
    v-model="partyDialogVisible"
    type="party"
    :categories="partyCategories"
    :documents="partyDocuments"
    @confirm="handlePartySelect"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileSelectorDialog from '@/components/FileSelectorDialog.vue'
import { useKnowledgeStore } from '@/stores/knowledgeStore'
import { usePartyStore } from '@/stores/partyStore'

// 文件选择对话框状态
const knowledgeDialogVisible = ref(false)
const partyDialogVisible = ref(false)

// Store
const knowledgeStore = useKnowledgeStore()
const partyStore = usePartyStore()

// 计算属性
const knowledgeCategories = computed(() => knowledgeStore.categoryTree)
const knowledgeDocuments = computed(() => knowledgeStore.documents)
const partyCategories = computed(() => partyStore.categoryTree)
const partyDocuments = computed(() => partyStore.documents)

// 方法
function handleSelectKnowledge() {
  knowledgeDialogVisible.value = true
  // 加载知识库数据
  knowledgeStore.loadCategoryTree()
  knowledgeStore.loadDocuments()
}

function handleSelectParty() {
  partyDialogVisible.value = true
  // 加载党建活动数据
  partyStore.loadCategoryTree()
  partyStore.loadDocuments()
}

function handleKnowledgeSelect(documentIds: string[]) {
  // 根据ID获取文档详情并添加到附件
  const selectedDocs = knowledgeDocuments.value.filter(d =>
    documentIds.includes(d.id)
  )

  for (const doc of selectedDocs) {
    if (!isAtMaxFiles.value) break
    attachments.value.push({
      id: doc.id,
      name: doc.original_filename,
      type: 'knowledge',
      size: doc.file_size,
      status: 'ready'
    })
  }

  ElMessage.success(`已添加 ${selectedDocs.length} 个文件`)
}

function handlePartySelect(documentIds: string[]) {
  // 类似知识库处理
  const selectedDocs = partyDocuments.value.filter(d =>
    documentIds.includes(d.id)
  )

  for (const doc of selectedDocs) {
    if (!isAtMaxFiles.value) break
    attachments.value.push({
      id: doc.id,
      name: doc.original_filename,
      type: 'party',
      size: doc.file_size,
      status: 'ready'
    })
  }

  ElMessage.success(`已添加 ${selectedDocs.length} 个文件`)
}
</script>
```

**Step 2: 提交**

```bash
git add frontend/src/components/ChatInput.vue
git commit -m "feat: 在ChatInput中集成文件选择对话框"
```

---

## 第四阶段：集成和测试

### Task 4.1: 更新聊天服务支持附件

**Files:**
- Modify: `frontend/src/services/chatApi.ts`

**Step 1: 扩展聊天 API 调用**

在 `frontend/src/services/chatApi.ts` 中更新发送消息函数:

```typescript
import type { AttachmentReference } from '@/types'

export async function sendMessage(
  toolId: string,
  message: string,
  sessionId?: string | null,
  history?: Message[],
  attachedFiles?: AttachmentReference[]
): Promise<ReadableStream> {
  const response = await fetch(`/api/v1/tools/${toolId}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      history,
      attached_files: attachedFiles  // 新增
    })
  })

  if (!response.ok) {
    throw new Error('发送消息失败')
  }

  return response.body!
}
```

**Step 2: 提交**

```bash
git add frontend/src/services/chatApi.ts
git commit -m "feat: 更新聊天服务支持附件"
```

---

### Task 4.2: E2E 测试

**Files:**
- Create: `frontend/tests/e2e/chat-attachments.spec.ts`

**Step 1: 创建 E2E 测试**

创建 `frontend/tests/e2e/chat-attachments.spec.ts`:

```typescript
import { test, expect } from '@playwright/test'

test.describe('聊天附件功能', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5173/login')
    await page.fill('input[name="account"]', 'test_user')
    await page.fill('input[name="password"]', 'test_password')
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:5173/')
  })

  test('应该显示文件操作按钮', async ({ page }) => {
    await page.goto('http://localhost:5173/tools/test-tool')

    await expect(page.locator('[data-test="upload-btn"]')).toBeVisible()
    await expect(page.locator('[data-test="knowledge-btn"]')).toBeVisible()
    await expect(page.locator('[data-test="party-btn"]')).toBeVisible()
  })

  test('应该能上传本地文件', async ({ page }) => {
    await page.goto('http://localhost:5173/tools/test-tool')

    // 创建测试文件
    const fileContent = 'This is a test file content.'
    const file = new File([fileContent], 'test.txt', { type: 'text/plain' })

    // 触发文件上传
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(file)

    // 验证附件显示
    await expect(page.locator('.attachment-tag')).toContainText('test.txt')
  })

  test('应该限制最多5个文件', async ({ page }) => {
    await page.goto('http://localhost:5173/tools/test-tool')

    // 尝试上传6个文件
    for (let i = 0; i < 6; i++) {
      const file = new File([`content ${i}`], `file${i}.txt`, { type: 'text/plain' })
      const fileInput = await page.locator('input[type="file"]')
      await fileInput.setInputFiles(file)
    }

    // 验证最多5个
    const attachments = await page.locator('.attachment-tag').count()
    expect(attachments).toBe(5)
  })

  test('发送消息后应该清空附件', async ({ page }) => {
    await page.goto('http://localhost:5173/tools/test-tool')

    // 上传文件
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(file)

    // 输入并发送消息
    await page.fill('textarea', '请分析附件内容')
    await page.click('.send-button')

    // 验证附件被清空
    await expect(page.locator('.attachment-tag')).toHaveCount(0)
  })
})
```

**Step 2: 运行 E2E 测试**

```bash
cd frontend && npm run test:e2e
```

**Step 3: 提交**

```bash
git add frontend/tests/e2e/chat-attachments.spec.ts
git commit -m "test: 添加聊天附件E2E测试"
```

---

## 验收检查清单

完成所有任务后，验证以下功能：

### 后端
- [ ] 临时文件上传成功，返回 temp_id
- [ ] 文件大小超过 10MB 时返回 400 错误
- [ ] 批量获取知识库文档成功
- [ ] 批量获取党建活动文档成功
- [ ] 聊天接口正确处理附件参数
- [ ] 附件内容正确注入到 AI system_prompt
- [ ] 定时清理临时文件正常工作

### 前端
- [ ] ChatInput 显示三个文件操作按钮
- [ ] 可以上传本地文件，显示进度和状态
- [ ] 可以从知识库选择文件
- [ ] 可以从党建活动选择文件
- [ ] 最多只能选择 5 个文件
- [ ] 单个文件超过 10MB 时有错误提示
- [ ] 可以删除已选附件
- [ ] 发送消息后附件列表自动清空
- [ ] 用户消息下方显示已发送的附件

### 测试
- [ ] 后端单元测试全部通过
- [ ] 后端集成测试全部通过
- [ ] 前端单元测试全部通过
- [ ] E2E 测试全部通过
- [ ] 使用独立测试数据库，不影响开发数据

---

## 相关文件

**后端**:
- `backend/src/config/temp_files.py` - 临时文件配置
- `backend/src/services/temp_file_service.py` - 临时文件服务
- `backend/src/interfaces/routers/temp_files/router.py` - 临时文件路由
- `backend/src/interfaces/routers/tools/chat.py` - 聊天接口（已修改）
- `backend/src/services/ai_service.py` - AI服务（已修改）

**前端**:
- `frontend/src/components/ChatInput.vue` - 聊天输入（已修改）
- `frontend/src/components/ChatPanel.vue` - 消息面板（已修改）
- `frontend/src/components/FileSelectorDialog.vue` - 文件选择对话框
- `frontend/src/services/tempFilesApi.ts` - 临时文件API
- `frontend/src/types/index.ts` - 类型定义（已修改）

**测试**:
- `backend/tests/unit/test_temp_file_service.py`
- `backend/tests/integration/test_temp_files_api.py`
- `backend/tests/integration/test_chat_with_attachments.py`
- `frontend/tests/unit/ChatInput.spec.ts`
- `frontend/tests/e2e/chat-attachments.spec.ts`
