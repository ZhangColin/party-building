"""
OpenAI Provider单元测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime
from openai import AsyncOpenAI

from src.infrastructure.providers.openai_provider import OpenAIProvider
from src.domain.entities.message import Message
from src.domain.value_objects.message_role import MessageRole


class TestOpenAIProvider:
    """测试OpenAIProvider实现"""

    def test_init_with_api_key(self):
        """测试使用API密钥初始化"""
        provider = OpenAIProvider(api_key="test-key")
        assert provider._api_key == "test-key"
        assert provider._base_url == "https://api.openai.com/v1"

    def test_init_with_custom_base_url(self):
        """测试使用自定义base_url初始化"""
        provider = OpenAIProvider(
            api_key="test-key",
            base_url="https://custom.openai.com/v1"
        )
        assert provider._base_url == "https://custom.openai.com/v1"

    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        provider = OpenAIProvider(api_key="test-key")
        models = provider.get_supported_models()

        assert "gpt-4" in models
        assert "gpt-4-turbo" in models
        assert "gpt-3.5-turbo" in models

    def test_validate_model(self):
        """测试模型验证"""
        provider = OpenAIProvider(api_key="test-key")

        # 支持的模型
        assert provider.validate_model("gpt-4") is True
        assert provider.validate_model("gpt-4-turbo") is True
        assert provider.validate_model("gpt-3.5-turbo") is True

        # 不支持的模型
        assert provider.validate_model("gpt-5") is False
        assert provider.validate_model("deepseek-chat") is False

    @pytest.mark.asyncio
    async def test_chat_stream_success(self):
        """测试流式对话成功"""
        provider = OpenAIProvider(api_key="test-key")

        # Mock AsyncOpenAI client
        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_response = AsyncMock()
        mock_response.choices = [MagicMock(delta=MagicMock(content="Hello"))]

        async def mock_stream(*args, **kwargs):
            chunks = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" "))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="World"))]),
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
        async for chunk in provider.chat_stream(messages, "gpt-4"):
            chunks.append(chunk)

        assert chunks == ["Hello", " ", "World"]

    @pytest.mark.asyncio
    async def test_chat_stream_with_temperature(self):
        """测试流式对话带温度参数"""
        provider = OpenAIProvider(api_key="test-key")

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

        async for _ in provider.chat_stream(messages, "gpt-4", temperature=0.5):
            pass

    @pytest.mark.asyncio
    async def test_chat_stream_with_max_tokens(self):
        """测试流式对话带max_tokens参数"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_stream(*args, **kwargs):
            assert kwargs.get("max_tokens") == 1000
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

        async for _ in provider.chat_stream(messages, "gpt-4", max_tokens=1000):
            pass

    @pytest.mark.asyncio
    async def test_chat_success(self):
        """测试非流式对话成功"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello World"))]

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

        response = await provider.chat(messages, "gpt-4")
        assert response == "Hello World"

    @pytest.mark.asyncio
    async def test_chat_with_temperature_and_max_tokens(self):
        """测试非流式对话带参数"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_create(*args, **kwargs):
            assert kwargs.get("temperature") == 0.3
            assert kwargs.get("max_tokens") == 500
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

        await provider.chat(messages, "gpt-4", temperature=0.3, max_tokens=500)

    @pytest.mark.asyncio
    async def test_generate_image_success(self):
        """测试图片生成成功"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="http://example.com/image.png")]

        mock_client.images.generate = AsyncMock(return_value=mock_response)
        provider._client = mock_client

        url = await provider.generate_image("A beautiful sunset", "1024x1024")
        assert url == "http://example.com/image.png"

    @pytest.mark.asyncio
    async def test_generate_image_with_custom_size(self):
        """测试图片生成带自定义尺寸"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_generate(*args, **kwargs):
            assert kwargs.get("size") == "512x512"
            assert kwargs.get("prompt") == "A cat"
            return MagicMock(data=[MagicMock(url="http://example.com/cat.png")])

        mock_client.images.generate = mock_generate
        provider._client = mock_client

        url = await provider.generate_image("A cat", "512x512")
        assert url == "http://example.com/cat.png"

    @pytest.mark.asyncio
    async def test_generate_audio_success(self):
        """测试音频生成成功"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_response = MagicMock()
        mock_response.content = b"fake audio content"

        # Mock base64.b64encode to return predictable result
        with patch("base64.b64encode", return_value=b"ZmFrZSBhdWRpbw=="):
            mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
            provider._client = mock_client

            result = await provider.generate_audio("Hello world", "alloy")
            # 应该返回base64编码的内容
            assert "ZmFrZSBhdWRpbw==" in result

    @pytest.mark.asyncio
    async def test_generate_audio_with_different_voice(self):
        """测试音频生成带不同音色"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        async def mock_create(*args, **kwargs):
            assert kwargs.get("voice") == "echo"
            assert kwargs.get("input") == "Test text"
            mock_resp = MagicMock()
            mock_resp.content = b"audio content"
            return mock_resp

        mock_client.audio.speech.create = mock_create
        provider._client = mock_client

        with patch("base64.b64encode", return_value=b"YXVkaW8="):
            await provider.generate_audio("Test text", "echo")

    @pytest.mark.asyncio
    async def test_messages_conversion_for_openai(self):
        """测试Message对象转换为OpenAI格式"""
        provider = OpenAIProvider(api_key="test-key")

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
                content="You are a helpful assistant",
                artifact=None,
                created_at=datetime.now()
            ),
            Message(
                id="msg2",
                session_id="session1",
                role=MessageRole.USER,
                content="Hello",
                artifact=None,
                created_at=datetime.now()
            )
        ]

        await provider.chat(messages, "gpt-4")

        # 验证消息格式转换
        assert captured_messages is not None
        assert len(captured_messages) == 2
        assert captured_messages[0]["role"] == "system"
        assert captured_messages[0]["content"] == "You are a helpful assistant"
        assert captured_messages[1]["role"] == "user"
        assert captured_messages[1]["content"] == "Hello"

    def test_provider_is_singleton_per_config(self):
        """测试相同配置返回同一client实例"""
        provider1 = OpenAIProvider(api_key="test-key")
        provider2 = OpenAIProvider(api_key="test-key")

        # 不同实例，但配置相同
        assert provider1 is not provider2
        assert provider1._api_key == provider2._api_key

    @pytest.mark.asyncio
    async def test_chat_stream_error_handling(self):
        """测试流式对话错误处理"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)

        # Mock create方法，让它返回一个会抛出异常的异步生成器
        async def error_stream():
            raise Exception("API Error")
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
        with pytest.raises(Exception, match="API Error"):
            async for _ in provider.chat_stream(messages, "gpt-4"):
                pass

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """测试非流式对话错误处理"""
        provider = OpenAIProvider(api_key="test-key")

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
            await provider.chat(messages, "gpt-4")

    @pytest.mark.asyncio
    async def test_generate_image_error_handling(self):
        """测试图片生成错误处理"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_client.images.generate = AsyncMock(
            side_effect=Exception("DALL-E Error")
        )
        provider._client = mock_client

        # 应该抛出异常
        with pytest.raises(Exception, match="DALL-E Error"):
            await provider.generate_image("A cat")

    @pytest.mark.asyncio
    async def test_generate_audio_error_handling(self):
        """测试音频生成错误处理"""
        provider = OpenAIProvider(api_key="test-key")

        mock_client = AsyncMock(spec=AsyncOpenAI)
        mock_client.audio.speech.create = AsyncMock(
            side_effect=Exception("TTS Error")
        )
        provider._client = mock_client

        # 应该抛出异常
        with pytest.raises(Exception, match="TTS Error"):
            await provider.generate_audio("Hello")
