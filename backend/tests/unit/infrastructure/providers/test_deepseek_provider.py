"""
DeepSeek Provider单元测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime
from openai import AsyncOpenAI

from src.infrastructure.providers.deepseek_provider import DeepSeekProvider
from src.domain.entities.message import Message
from src.domain.value_objects.message_role import MessageRole


class TestDeepSeekProvider:
    """测试DeepSeekProvider实现"""

    def test_init_with_api_key(self):
        """测试使用API密钥初始化"""
        provider = DeepSeekProvider(api_key="test-key")
        assert provider._api_key == "test-key"
        assert provider._base_url == "https://api.deepseek.com"

    def test_init_with_custom_base_url(self):
        """测试使用自定义base_url初始化"""
        provider = DeepSeekProvider(
            api_key="test-key",
            base_url="https://custom.deepseek.com"
        )
        assert provider._base_url == "https://custom.deepseek.com"

    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        provider = DeepSeekProvider(api_key="test-key")
        models = provider.get_supported_models()

        assert "deepseek-chat" in models
        assert "deepseek-coder" in models

    def test_validate_model(self):
        """测试模型验证"""
        provider = DeepSeekProvider(api_key="test-key")

        # 支持的模型
        assert provider.validate_model("deepseek-chat") is True
        assert provider.validate_model("deepseek-coder") is True

        # 不支持的模型
        assert provider.validate_model("gpt-4") is False
        assert provider.validate_model("deepseek-v3") is False

    @pytest.mark.asyncio
    async def test_chat_stream_success(self):
        """测试流式对话成功"""
        provider = DeepSeekProvider(api_key="test-key")

        # Mock AsyncOpenAI client
        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_stream(*args, **kwargs):
            chunks = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" "))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="DeepSeek"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=None))])
            ]
            for chunk in chunks:
                yield chunk

        mock_client.chat.completions.create = mock_stream
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Hello",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        # 测试流式响应
        chunks = []
        async for chunk in provider.chat_stream(messages, "deepseek-chat"):
            chunks.append(chunk)

        assert chunks == ["Hello", " ", "DeepSeek"]

    @pytest.mark.asyncio
    async def test_chat_stream_with_temperature(self):
        """测试流式对话带温度参数"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_stream(*args, **kwargs):
            # 验证参数传递
            assert kwargs.get("temperature") == 0.5
            yield MagicMock(choices=[MagicMock(delta=MagicMock(content="response"))])

        mock_client.chat.completions.create = mock_stream
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Test",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        async for _ in provider.chat_stream(messages, "deepseek-chat", temperature=0.5):
            pass

    @pytest.mark.asyncio
    async def test_chat_stream_with_max_tokens(self):
        """测试流式对话带max_tokens参数"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_stream(*args, **kwargs):
            assert kwargs.get("max_tokens") == 2000
            yield MagicMock(choices=[MagicMock(delta=MagicMock(content="response"))])

        mock_client.chat.completions.create = mock_stream
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Test",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        async for _ in provider.chat_stream(messages, "deepseek-coder", max_tokens=2000):
            pass

    @pytest.mark.asyncio
    async def test_chat_success(self):
        """测试非流式对话成功"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="DeepSeek response"))]

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Hello",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        response = await provider.chat(messages, "deepseek-chat")
        assert response == "DeepSeek response"

    @pytest.mark.asyncio
    async def test_chat_with_temperature_and_max_tokens(self):
        """测试非流式对话带参数"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_create(*args, **kwargs):
            assert kwargs.get("temperature") == 0.3
            assert kwargs.get("max_tokens") == 1000
            return MagicMock(choices=[MagicMock(message=MagicMock(content="response"))])

        mock_client.chat.completions.create = mock_create
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Test",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        await provider.chat(messages, "deepseek-chat", temperature=0.3, max_tokens=1000)

    @pytest.mark.asyncio
    async def test_generate_image_not_implemented(self):
        """测试图片生成抛出NotImplementedError"""
        provider = DeepSeekProvider(api_key="test-key")

        with pytest.raises(NotImplementedError) as exc_info:
            await provider.generate_image("A test image")

        assert "image generation" in str(exc_info.value).lower()
        assert "deepseek" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_audio_not_implemented(self):
        """测试音频生成抛出NotImplementedError"""
        provider = DeepSeekProvider(api_key="test-key")

        with pytest.raises(NotImplementedError) as exc_info:
            await provider.generate_audio("Test text")

        assert "audio generation" in str(exc_info.value).lower()
        assert "deepseek" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_messages_conversion_for_deepseek(self):
        """测试Message对象转换为DeepSeek格式"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        captured_messages = None

        async def mock_create(*args, **kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get("messages")
            return MagicMock(choices=[MagicMock(message=MagicMock(content="OK"))])

        mock_client.chat.completions.create = mock_create
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.SYSTEM,
                content="You are a coding assistant",
                artifact=None,
                created_at=datetime.now()
            ),
            Message(
                id="msg2",
                session_id="session1",
                role=MessageRole.USER,
                content="Write Python code",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        await provider.chat(messages, "deepseek-coder")

        # 验证消息格式转换
        assert captured_messages is not None
        assert len(captured_messages) == 2
        assert captured_messages[0]["role"] == "system"
        assert captured_messages[0]["content"] == "You are a coding assistant"
        assert captured_messages[1]["role"] == "user"
        assert captured_messages[1]["content"] == "Write Python code"

    @pytest.mark.asyncio
    async def test_deepseek_coder_model_chat(self):
        """测试使用deepseek-coder模型进行对话"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_create(*args, **kwargs):
            assert kwargs.get("model") == "deepseek-coder"
            return MagicMock(choices=[MagicMock(message=MagicMock(content="Code here"))])

        mock_client.chat.completions.create = mock_create
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Write a function",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        response = await provider.chat(messages, "deepseek-coder")
        assert response == "Code here"

    def test_deepseek_uses_openai_compatible_api(self):
        """测试DeepSeek使用OpenAI兼容API"""
        provider = DeepSeekProvider(api_key="test-key")

        # 验证客户端类型
        assert isinstance(provider._client, AsyncOpenAI)
        assert provider._client.api_key == "test-key"
        assert provider._client.base_url == "https://api.deepseek.com"

    @pytest.mark.asyncio
    async def test_chat_stream_error_handling(self):
        """测试流式对话错误处理"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        # Mock create方法，让它返回一个会抛出异常的异步生成器
        async def error_stream():
            raise Exception("DeepSeek API Error")
            yield

        mock_client.chat.completions.create = lambda *args, **kwargs: error_stream()
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Test",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        # 应该抛出异常
        with pytest.raises(Exception, match="DeepSeek API Error"):
            async for _ in provider.chat_stream(messages, "deepseek-chat"):
                pass

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """测试非流式对话错误处理"""
        provider = DeepSeekProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Network Error")
        )
        provider._client = mock_client

        messages = [
            Message(
                id="msg1",
                session_id="session1",
                role=MessageRole.USER,
                content="Test",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        # 应该抛出异常
        with pytest.raises(Exception, match="Network Error"):
            await provider.chat(messages, "deepseek-chat")
