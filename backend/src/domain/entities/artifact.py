"""
Artifact领域实体（临时占位）

Artifact表示AI生成的成果物（HTML/SVG/Markdown等）
TODO: 在后续任务中完善
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Artifact:
    """成果物实体（临时）"""
    id: str
    type: str  # "html", "svg", "markdown"
    content: str
    created_at: datetime
