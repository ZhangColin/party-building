"""
AIProvider抽象基类

定义AI提供商的统一接口，支持多模型接入
"""
from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Optional

from src.domain.entities.message import Message


class AIProvider(ABC):
    """
    AI提供商抽象接口

    所有AI提供商（OpenAI、DeepSeek、Kimi等）都必须实现此接口
    """

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Yields:
            str: 流式返回的文本片段
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        非流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            str: 完整的AI响应文本
        """
        pass

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """
        生成图片

        Args:
            prompt: 图片描述提示词
            size: 图片尺寸
            **kwargs: 其他参数

        Returns:
            str: 图片URL或base64编码
        """
        pass

    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice: str = "alloy",
        **kwargs
    ) -> str:
        """
        生成音频

        Args:
            text: 要转换为音频的文本
            voice: 音色/声音
            **kwargs: 其他参数

        Returns:
            str: 音频文件URL或base64编码
        """
        pass

    def get_supported_models(self) -> List[str]:
        """
        获取支持的模型列表

        Returns:
            List[str]: 支持的模型名称列表
        """
        return []

    def validate_model(self, model: str) -> bool:
        """
        验证模型是否支持

        Args:
            model: 模型名称

        Returns:
            bool: 是否支持该模型
        """
        return model in self.get_supported_models()
