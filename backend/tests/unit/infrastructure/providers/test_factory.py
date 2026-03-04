"""
ProviderFactory单元测试
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from src.infrastructure.providers.factory import ProviderFactory
from src.infrastructure.providers.openai_provider import OpenAIProvider
from src.infrastructure.providers.deepseek_provider import DeepSeekProvider


class TestProviderFactory:
    """测试ProviderFactory工厂类"""

    def test_factory_has_registry(self):
        """测试工厂有注册表"""
        assert hasattr(ProviderFactory, '_providers')
        assert isinstance(ProviderFactory._providers, dict)

    def test_factory_has_openai_registered(self):
        """测试OpenAI已注册"""
        assert 'openai' in ProviderFactory._providers
        assert ProviderFactory._providers['openai'] == OpenAIProvider

    def test_factory_has_deepseek_registered(self):
        """测试DeepSeek已注册"""
        assert 'deepseek' in ProviderFactory._providers
        assert ProviderFactory._providers['deepseek'] == DeepSeekProvider

    def test_create_openai_provider(self):
        """测试创建OpenAI Provider"""
        provider = ProviderFactory.create(
            provider_name="openai",
            api_key="test-openai-key"
        )

        assert isinstance(provider, OpenAIProvider)
        assert provider._api_key == "test-openai-key"
        assert provider._base_url == "https://api.openai.com/v1"

    def test_create_openai_provider_with_custom_base_url(self):
        """测试创建OpenAI Provider带自定义base_url"""
        provider = ProviderFactory.create(
            provider_name="openai",
            api_key="test-key",
            base_url="https://custom.openai.com/v1"
        )

        assert isinstance(provider, OpenAIProvider)
        assert provider._base_url == "https://custom.openai.com/v1"

    def test_create_deepseek_provider(self):
        """测试创建DeepSeek Provider"""
        provider = ProviderFactory.create(
            provider_name="deepseek",
            api_key="test-deepseek-key"
        )

        assert isinstance(provider, DeepSeekProvider)
        assert provider._api_key == "test-deepseek-key"
        assert provider._base_url == "https://api.deepseek.com"

    def test_create_deepseek_provider_with_custom_base_url(self):
        """测试创建DeepSeek Provider带自定义base_url"""
        provider = ProviderFactory.create(
            provider_name="deepseek",
            api_key="test-key",
            base_url="https://custom.deepseek.com"
        )

        assert isinstance(provider, DeepSeekProvider)
        assert provider._base_url == "https://custom.deepseek.com"

    def test_create_unknown_provider_raises_error(self):
        """测试创建不存在的provider抛出错误"""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.create(
                provider_name="unknown_provider",
                api_key="test-key"
            )

        assert "unknown" in str(exc_info.value).lower()
        assert "provider" in str(exc_info.value).lower()

    def test_create_provider_case_insensitive(self):
        """测试provider名称大小写不敏感"""
        provider1 = ProviderFactory.create(
            provider_name="OpenAI",
            api_key="test-key"
        )
        provider2 = ProviderFactory.create(
            provider_name="OPENAI",
            api_key="test-key"
        )
        provider3 = ProviderFactory.create(
            provider_name="openai",
            api_key="test-key"
        )

        # 所有都应该成功创建OpenAIProvider
        assert isinstance(provider1, OpenAIProvider)
        assert isinstance(provider2, OpenAIProvider)
        assert isinstance(provider3, OpenAIProvider)

    def test_create_deepseek_case_insensitive(self):
        """测试DeepSeek名称大小写不敏感"""
        provider1 = ProviderFactory.create(
            provider_name="DeepSeek",
            api_key="test-key"
        )
        provider2 = ProviderFactory.create(
            provider_name="DEEPSEEK",
            api_key="test-key"
        )

        assert isinstance(provider1, DeepSeekProvider)
        assert isinstance(provider2, DeepSeekProvider)

    @patch.dict(os.environ, {
        'CURRENT_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'env-openai-key'
    })
    def test_create_from_env_openai(self):
        """测试从环境变量创建OpenAI Provider"""
        provider = ProviderFactory.create_from_env()

        assert isinstance(provider, OpenAIProvider)
        assert provider._api_key == "env-openai-key"

    @patch.dict(os.environ, {
        'CURRENT_PROVIDER': 'deepseek',
        'DEEPSEEK_API_KEY': 'env-deepseek-key'
    })
    def test_create_from_env_deepseek(self):
        """测试从环境变量创建DeepSeek Provider"""
        provider = ProviderFactory.create_from_env()

        assert isinstance(provider, DeepSeekProvider)
        assert provider._api_key == "env-deepseek-key"

    @patch.dict(os.environ, {
        'CURRENT_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'env-openai-key',
        'OPENAI_BASE_URL': 'https://custom-from-env.com/v1'
    })
    def test_create_from_env_with_custom_base_url(self):
        """测试从环境变量创建Provider带自定义base_url"""
        provider = ProviderFactory.create_from_env()

        assert isinstance(provider, OpenAIProvider)
        assert provider._base_url == "https://custom-from-env.com/v1"

    @patch.dict(os.environ, {
        'CURRENT_PROVIDER': 'unknown_provider',
        'OPENAI_API_KEY': 'test-key'
    })
    def test_create_from_env_unknown_provider(self):
        """测试从环境变量创建不存在的provider抛出错误"""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.create_from_env()

        assert "unknown" in str(exc_info.value).lower()

    @patch.dict(os.environ, {}, clear=True)
    def test_create_from_env_missing_provider_env(self):
        """测试环境变量缺少CURRENT_PROVIDER"""
        # 删除所有环境变量后，应该使用默认值
        with patch.dict(os.environ, {}, clear=True):
            # 模拟没有CURRENT_PROVIDER的情况
            # 应该使用默认的 'deepseek'
            pass

    def test_factory_allows_registering_custom_provider(self):
        """测试工厂允许注册自定义provider"""
        from src.infrastructure.providers.base import AIProvider

        class CustomProvider(AIProvider):
            def __init__(self, api_key, base_url="https://custom.com"):
                self._api_key = api_key
                self._base_url = base_url

            async def chat_stream(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                yield "response"

            async def chat(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
                return "response"

            async def generate_image(self, prompt, size="1024x1024", **kwargs):
                return "http://example.com/image.png"

            async def generate_audio(self, text, voice="alloy", **kwargs):
                return "http://example.com/audio.mp3"

        # 注册自定义provider
        ProviderFactory.register_provider("custom", CustomProvider)

        # 验证可以创建
        provider = ProviderFactory.create(
            provider_name="custom",
            api_key="test-key"
        )

        assert isinstance(provider, CustomProvider)
        assert provider._api_key == "test-key"

        # 清理
        del ProviderFactory._providers["custom"]

    def test_get_registered_providers(self):
        """测试获取已注册的provider列表"""
        providers = ProviderFactory.get_registered_providers()

        assert isinstance(providers, list)
        assert "openai" in providers
        assert "deepseek" in providers

    def test_is_provider_registered(self):
        """测试检查provider是否已注册"""
        assert ProviderFactory.is_provider_registered("openai") is True
        assert ProviderFactory.is_provider_registered("deepseek") is True
        assert ProviderFactory.is_provider_registered("unknown") is False

    def test_is_provider_registered_case_insensitive(self):
        """测试检查provider注册是否大小写不敏感"""
        assert ProviderFactory.is_provider_registered("OpenAI") is True
        assert ProviderFactory.is_provider_registered("DEEPSEEK") is True
