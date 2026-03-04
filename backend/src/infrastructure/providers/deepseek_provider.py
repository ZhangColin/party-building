"""
DeepSeek Provider实现

提供DeepSeek API的实现，DeepSeek兼容OpenAI协议
专注于对话能力，不支持多模态生成
"""
import logging
from typing import List, AsyncGenerator, Optional

from openai import AsyncOpenAI

from src.infrastructure.providers.base import AIProvider
from src.domain.entities.message import Message
from src.domain.value_objects.message_role import MessageRole

logger = logging.getLogger(__name__)


class DeepSeekProvider(AIProvider):
    """
    DeepSeek API提供商实现

    DeepSeek专注于对话能力，兼容OpenAI协议
    - 支持流式和非流式对话
    - 不支持图片生成（使用NotImplementedError）
    - 不支持音频生成（使用NotImplementedError）

    支持的模型：
    - deepseek-chat: 通用对话模型
    - deepseek-coder: 代码专用模型
    """

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek Provider

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL（默认为DeepSeek官方API地址）
        """
        self._api_key = api_key
        self._base_url = base_url
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        logger.info(f"DeepSeek Provider initialized with base_url: {base_url}")

    def get_supported_models(self) -> List[str]:
        """
        获取支持的模型列表

        Returns:
            List[str]: DeepSeek模型列表
        """
        return ["deepseek-chat", "deepseek-coder"]

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
        try:
            # 转换消息格式
            deepseek_messages = self._convert_messages(messages)

            # 调用DeepSeek API (stream=True返回async generator)
            stream = self._client.chat.completions.create(
                model=model,
                messages=deepseek_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            # 流式返回内容
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"DeepSeek stream chat error: {e}")
            raise

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
        try:
            # 转换消息格式
            deepseek_messages = self._convert_messages(messages)

            # 调用DeepSeek API
            response = await self._client.chat.completions.create(
                model=model,
                messages=deepseek_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek chat error: {e}")
            raise

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """
        生成图片

        DeepSeek不支持图片生成，抛出NotImplementedError

        Args:
            prompt: 图片描述提示词
            size: 图片尺寸
            **kwargs: 其他参数

        Returns:
            str: 图片URL

        Raises:
            NotImplementedError: DeepSeek不支持图片生成
        """
        raise NotImplementedError(
            "DeepSeek does not support image generation. "
            "Please use a provider that supports multimodal capabilities like OpenAI."
        )

    async def generate_audio(
        self,
        text: str,
        voice: str = "alloy",
        **kwargs
    ) -> str:
        """
        生成音频

        DeepSeek不支持音频生成，抛出NotImplementedError

        Args:
            text: 要转换为音频的文本
            voice: 音色/声音
            **kwargs: 其他参数

        Returns:
            str: 音频文件URL或base64编码

        Raises:
            NotImplementedError: DeepSeek不支持音频生成
        """
        raise NotImplementedError(
            "DeepSeek does not support audio generation. "
            "Please use a provider that supports multimodal capabilities like OpenAI."
        )

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """
        将Message对象列表转换为DeepSeek API格式

        Args:
            messages: Message对象列表

        Returns:
            List[dict]: DeepSeek格式的消息列表（与OpenAI格式相同）
        """
        deepseek_messages = []

        for message in messages:
            msg_dict = {
                "role": self._convert_role(message.role),
                "content": message.content
            }
            deepseek_messages.append(msg_dict)

        return deepseek_messages

    def _convert_role(self, role: MessageRole) -> str:
        """
        转换消息角色

        Args:
            role: MessageRole枚举

        Returns:
            str: DeepSeek格式的角色字符串（与OpenAI格式相同）
        """
        if role.is_system_message():
            return "system"
        elif role.is_user_message():
            return "user"
        elif role.is_assistant_message():
            return "assistant"
        else:
            return "user"  # 默认为user
