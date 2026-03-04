"""
ProviderFactory工厂类

提供统一的Provider创建接口，支持环境变量配置
"""
import os
import logging
from typing import Type, Dict, List

from src.infrastructure.providers.base import AIProvider
from src.infrastructure.providers.openai_provider import OpenAIProvider
from src.infrastructure.providers.deepseek_provider import DeepSeekProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    AI Provider工厂类

    负责创建和管理AI Provider实例
    - 支持通过名称创建Provider
    - 支持从环境变量创建Provider
    - Provider注册表管理
    """

    # Provider注册表：provider名称 -> Provider类
    _providers: Dict[str, Type[AIProvider]] = {
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        base_url: str = None,
        **kwargs
    ) -> AIProvider:
        """
        创建Provider实例

        Args:
            provider_name: Provider名称（openai, deepseek等）
            api_key: API密钥
            base_url: 可选的自定义base_url
            **kwargs: 其他传递给Provider构造函数的参数

        Returns:
            AIProvider: Provider实例

        Raises:
            ValueError: 当provider_name未注册时
        """
        # 大小写不敏感
        provider_name_lower = provider_name.lower()

        if provider_name_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name_lower]

        # 构造函数参数
        init_kwargs = {"api_key": api_key}
        if base_url:
            init_kwargs["base_url"] = base_url
        init_kwargs.update(kwargs)

        provider = provider_class(**init_kwargs)
        logger.info(f"Created {provider_name} provider")
        return provider

    @classmethod
    def create_from_env(cls) -> AIProvider:
        """
        从环境变量创建Provider实例

        环境变量：
        - CURRENT_PROVIDER: provider名称（openai, deepseek等）
        - {PROVIDER}_API_KEY: 对应provider的API密钥
        - {PROVIDER}_BASE_URL: 可选的自定义base_url

        Returns:
            AIProvider: Provider实例

        Raises:
            ValueError: 当provider未配置或未注册时
        """
        provider_name = os.getenv("CURRENT_PROVIDER", "deepseek").lower()

        # 构造环境变量前缀
        env_prefix = provider_name.upper()

        # 获取API密钥
        api_key_env = f"{env_prefix}_API_KEY"
        api_key = os.getenv(api_key_env)

        if not api_key:
            raise ValueError(
                f"Missing API key for provider '{provider_name}'. "
                f"Please set environment variable: {api_key_env}"
            )

        # 获取可选的base_url
        base_url_env = f"{env_prefix}_BASE_URL"
        base_url = os.getenv(base_url_env)

        # 创建Provider
        return cls.create(
            provider_name=provider_name,
            api_key=api_key,
            base_url=base_url
        )

    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[AIProvider]
    ) -> None:
        """
        注册新的Provider

        Args:
            name: Provider名称
            provider_class: Provider类（必须继承AIProvider）

        Raises:
            TypeError: 当provider_class不是AIProvider的子类时
        """
        if not issubclass(provider_class, AIProvider):
            raise TypeError(
                f"Provider class must inherit from AIProvider. "
                f"Got: {provider_class}"
            )

        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered provider: {name}")

    @classmethod
    def get_registered_providers(cls) -> List[str]:
        """
        获取已注册的Provider列表

        Returns:
            List[str]: Provider名称列表
        """
        return list(cls._providers.keys())

    @classmethod
    def is_provider_registered(cls, provider_name: str) -> bool:
        """
        检查Provider是否已注册

        Args:
            provider_name: Provider名称

        Returns:
            bool: 是否已注册
        """
        return provider_name.lower() in cls._providers
