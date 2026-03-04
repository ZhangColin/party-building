"""
AIProvider抽象类测试
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.infrastructure.providers.base import AIProvider
from src.domain.entities.message import Message, MessageRole


class TestAIProvider:
    """测试AIProvider抽象类定义"""

    def test_ai_provider_is_abstract(self):
        """测试AIProvider是抽象类，无法直接实例化"""
        with pytest.raises(TypeError):
            AIProvider()

    def test_ai_provider_has_required_methods(self):
        """测试AIProvider定义了所有必需的抽象方法"""
        abstract_methods = AIProvider.__abstractmethods__
        expected_methods = {
            'chat_stream',
            'chat',
            'generate_image',
            'generate_audio'
        }
        assert abstract_methods == expected_methods

    def test_concrete_implementation_can_be_created(self):
        """测试可以创建具体的实现类"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(
                self,
                messages,
                model,
                temperature=0.7,
                max_tokens=None,
                **kwargs
            ):
                yield "Hello"

            async def chat(
                self,
                messages,
                model,
                temperature=0.7,
                max_tokens=None,
                **kwargs
            ):
                return "Hello"

            async def generate_image(
                self,
                prompt,
                size="1024x1024",
                **kwargs
            ):
                return "http://example.com/image.png"

            async def generate_audio(
                self,
                text,
                voice="alloy",
                **kwargs
            ):
                return "http://example.com/audio.mp3"

        # 应该能够实例化具体实现
        provider = ConcreteAIProvider()
        assert isinstance(provider, AIProvider)

    @pytest.mark.asyncio
    async def test_chat_stream_method(self):
        """测试chat_stream方法签名"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(
                self,
                messages,
                model,
                temperature=0.7,
                max_tokens=None,
                **kwargs
            ):
                for word in ["Hello", " ", "World"]:
                    yield word

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "Hello World"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()
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
    async def test_chat_method(self):
        """测试chat方法签名"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "Hello World"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()
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

        # 测试非流式响应
        response = await provider.chat(messages, "gpt-4")
        assert response == "Hello World"

    @pytest.mark.asyncio
    async def test_generate_image_method(self):
        """测试generate_image方法签名"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()

        # 测试图片生成
        url = await provider.generate_image("A beautiful sunset", "1024x1024")
        assert url == "http://example.com/image.png"

        # 测试不同尺寸
        url = await provider.generate_image("A cat", "512x512")
        assert url == "http://example.com/image.png"

    @pytest.mark.asyncio
    async def test_generate_audio_method(self):
        """测试generate_audio方法签名"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()

        # 测试音频生成
        url = await provider.generate_audio("Hello world", "alloy")
        assert url == "http://example.com/audio.mp3"

        # 测试不同音色
        url = await provider.generate_audio("Hello world", "echo")
        assert url == "http://example.com/audio.mp3"

    def test_get_supported_models_default(self):
        """测试get_supported_models默认返回空列表"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()
        models = provider.get_supported_models()
        assert models == []

    def test_validate_model_default(self):
        """测试validate_model默认行为"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()

        # 默认情况下，没有支持的模型
        assert provider.validate_model("gpt-4") is False
        assert provider.validate_model("any-model") is False

    def test_validate_model_with_supported_models(self):
        """测试validate_model与get_supported_models的集成"""
        class ConcreteAIProvider(AIProvider):
            """具体的AIProvider实现"""

            def get_supported_models(self):
                return ["gpt-4", "gpt-3.5-turbo", "deepseek-chat"]

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        provider = ConcreteAIProvider()

        # 测试支持的模型
        assert provider.validate_model("gpt-4") is True
        assert provider.validate_model("gpt-3.5-turbo") is True
        assert provider.validate_model("deepseek-chat") is True

        # 测试不支持的模型
        assert provider.validate_model("gpt-5") is False
        assert provider.validate_model("unknown-model") is False
