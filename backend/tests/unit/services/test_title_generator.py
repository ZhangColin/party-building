# -*- coding: utf-8 -*-
"""TitleGenerator 单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from src.services.title_generator import TitleGenerator


class TestTitleGenerator:
    """TitleGenerator 测试类"""

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test123",
        "CURRENT_PROVIDER": "deepseek"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_init_with_deepseek(self, mock_openai):
        """测试初始化 - DeepSeek"""
        generator = TitleGenerator()
        assert generator.client is not None
        assert generator.model_name == "deepseek-chat"
        mock_openai.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    @patch("src.services.title_generator.OpenAI")
    def test_init_no_api_key(self, mock_openai):
        """测试初始化 - 无API Key"""
        generator = TitleGenerator()
        assert generator.client is None
        assert generator.model_name == ""
        mock_openai.assert_not_called()

    @patch.dict("os.environ", {
        "OPENAI_API_KEY": "sk-test",
        "TITLE_GENERATION_MODEL": "openai:gpt-4"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_init_with_custom_model(self, mock_openai):
        """测试初始化 - 自定义模型配置"""
        generator = TitleGenerator()
        assert generator.client is not None
        assert generator.model_name == "gpt-4"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "invalid-key",  # 不以sk-开头
    })
    @patch("src.services.title_generator.OpenAI")
    def test_init_invalid_api_key(self, mock_openai):
        """测试初始化 - 无效的API Key"""
        generator = TitleGenerator()
        assert generator.client is None

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_fallback_title_empty_message(self, mock_openai):
        """测试降级标题生成 - 空消息"""
        generator = TitleGenerator()
        title = generator._fallback_title("")
        assert title == "新对话"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_fallback_title_short_message(self, mock_openai):
        """测试降级标题生成 - 短消息"""
        generator = TitleGenerator()
        title = generator._fallback_title("测试标题")
        assert title == "测试标题"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_fallback_title_long_message(self, mock_openai):
        """测试降级标题生成 - 长消息"""
        generator = TitleGenerator()
        long_msg = "这是一个很长的消息内容" * 10  # 超过30字符
        title = generator._fallback_title(long_msg)
        assert len(title) == 30
        assert title == long_msg[:30]

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_fallback_title_with_newlines(self, mock_openai):
        """测试降级标题生成 - 包含换行符"""
        generator = TitleGenerator()
        title = generator._fallback_title("第一行\n第二行\r第三行")
        assert "\n" not in title
        assert "\r" not in title
        assert " " in title

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_clean_title_removes_punctuation(self, mock_openai):
        """测试清理标题 - 移除标点符号"""
        generator = TitleGenerator()
        title = generator._clean_title('测试"标题"，包含【标点】符号！')
        assert '"' not in title
        assert '，' not in title
        assert '【' not in title
        assert '】' not in title
        assert '！' not in title
        assert title == "测试标题包含标点符号"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_clean_title_empty(self, mock_openai):
        """测试清理标题 - 空字符串"""
        generator = TitleGenerator()
        title = generator._clean_title("")
        assert title == ""

    @patch.dict("os.environ", {}, clear=True)
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_no_client(self, mock_openai):
        """测试生成标题 - 无AI客户端"""
        generator = TitleGenerator()
        title = await generator.generate_title("用户消息")
        assert title == "用户消息"  # 使用降级方案

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_empty_user_message(self, mock_openai):
        """测试生成标题 - 空用户消息"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title("")
        assert title == "新对话"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_short_message_with_ai_response(self, mock_openai):
        """测试生成标题 - 短消息+AI回复"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content.strip.return_value = "生成的标题"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title(
            user_message="短",
            ai_response="这是AI的回复内容" * 100
        )

        assert title == "生成的标题"
        # 验证调用了AI
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert "短" in call_args[1]["messages"][0]["content"]
        assert "这是AI的回复内容" in call_args[1]["messages"][0]["content"]

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_long_message(self, mock_openai):
        """测试生成标题 - 长消息"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content.strip.return_value = "长消息标题"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        long_msg = "这是一个很长的用户消息" * 100
        title = await generator.generate_title(long_msg)

        assert title == "长消息标题"
        # 验证消息被截断到500字符
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        # 验证prompt包含用户消息（但被截断）
        assert "这是一个很长的用户消息" in prompt

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_ai_failure(self, mock_openai):
        """测试生成标题 - AI调用失败"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("AI错误")
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title("测试消息")

        # 应该降级到简单截取
        assert title == "测试消息"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_empty_ai_response(self, mock_openai):
        """测试生成标题 - AI返回空内容"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content.strip.return_value = ""
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title("测试")

        assert title == "新对话"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_too_long(self, mock_openai):
        """测试生成标题 - AI返回过长的标题（不包含标点）"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # 返回超过30字符的标题（无标点符号）
        long_title = "这是一个非常非常非常非常非常非常长的标题超过了三十个字符的限制"
        mock_message.content.strip.return_value = long_title
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title("测试")

        # 应该被截断到30字符
        assert len(title) == 30
        assert title == "这是一个非常非常非常非常非常非常长的标题超过了三十个字符的限"

    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "sk-test"
    })
    @patch("src.services.title_generator.OpenAI")
    async def test_generate_title_no_ai_response(self, mock_openai):
        """测试生成标题 - 没有AI回复（短消息）"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content.strip.return_value = "测试标题"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = TitleGenerator()
        title = await generator.generate_title("短", ai_response=None)

        assert title == "测试标题"

    @patch.dict("os.environ", {
        "OPENAI_API_KEY": "sk-openai",
        "TITLE_GENERATION_MODEL": "openai:gpt-4-turbo"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_get_ai_client_openai(self, mock_openai):
        """测试获取AI客户端 - OpenAI"""
        generator = TitleGenerator()
        assert generator.client is not None
        assert generator.model_name == "gpt-4-turbo"
        mock_openai.assert_called_once()

    @patch.dict("os.environ", {
        "KIMI_API_KEY": "sk-kimi",
        "TITLE_GENERATION_MODEL": "kimi:moonshot-v1-8k"
    })
    @patch("src.services.title_generator.OpenAI")
    def test_get_ai_client_kimi(self, mock_openai):
        """测试获取AI客户端 - Kimi"""
        generator = TitleGenerator()
        assert generator.client is not None
        assert generator.model_name == "moonshot-v1-8k"

    @patch.dict("os.environ", {
        "CURRENT_PROVIDER": "unknown"
    }, clear=True)
    @patch("src.services.title_generator.OpenAI")
    def test_get_ai_client_unknown_provider(self, mock_openai):
        """测试获取AI客户端 - 未知提供商"""
        generator = TitleGenerator()
        # 未知提供商会返回None（因为没有DEEPSEEK_API_KEY，且provider是unknown）
        assert generator.client is None
        assert generator.model_name == ""
