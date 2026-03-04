"""
会话标题生成测试
Bug: 新开会话后，标题生成逻辑不正确

需求：
1. 用户输入简单/无意义（< 10字符）时，使用生成的内容让AI生成标题
2. 用户输入长且有意义时，按用户输入的内容让AI生成标题
3. 只有生成标题失败时，才截取用户输入作为兜底
"""
import pytest
from unittest.mock import Mock, patch
from src.services.title_generator import TitleGenerator


class TestTitleGenerator:
    """标题生成器测试"""

    @pytest.fixture
    def title_generator(self):
        """创建标题生成器实例"""
        return TitleGenerator()

    def test_should_use_user_message_for_long_input(self, title_generator):
        """
        测试1：用户输入长消息（>= 10字符）时，应该只使用用户消息生成标题
        """
        # Arrange
        user_message = "请帮我创建一个关于Photoshop调色的教学课件"
        ai_response = "这是生成的课件内容..." * 100  # 很长的AI回复

        # Mock AI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Photoshop调色教学课件"
        mock_client.chat.completions.create.return_value = mock_response

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert
        assert title == "Photoshop调色教学课件"

        # 验证AI调用时只使用了用户消息，没有使用AI回复
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        # 应该包含用户消息
        assert "Photoshop调色教学课件" in prompt or "请帮我创建" in prompt
        # 不应该包含AI回复（因为用户消息已经 >= 10字符）
        assert "这是生成的课件内容" not in prompt

    def test_should_use_ai_response_for_short_input(self, title_generator):
        """
        测试2：用户输入短消息（< 10字符）时，应该使用用户消息+AI回复生成标题
        """
        # Arrange
        user_message = "你好"
        ai_response = "这是一个关于AI助手的介绍，它可以帮你创建教学课件和生成练习题。"

        # Mock AI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI助手介绍"
        mock_client.chat.completions.create.return_value = mock_response

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert
        assert title == "AI助手介绍"

        # 验证AI调用时同时使用了用户消息和AI回复
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        # 应该同时包含用户消息和AI回复
        assert "你好" in prompt
        assert "AI助手" in prompt or "教学课件" in prompt

    def test_should_fallback_when_ai_fails(self, title_generator):
        """
        测试3：AI生成失败时，应该使用降级方案（截取用户输入）
        """
        # Arrange
        user_message = "这是一个非常长的用户输入，用来测试降级方案是否正常工作"  # 27个字符
        ai_response = "AI回复内容"

        # Mock AI客户端抛出异常
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("AI服务不可用")

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert - 应该使用降级方案，返回完整用户输入（27字符 < 30）
        assert title == "这是一个非常长的用户输入，用来测试降级方案是否正常工作"

    def test_should_truncate_long_user_message_in_fallback(self, title_generator):
        """
        测试4：降级方案中，超长用户消息应该被截取到30个字符
        """
        # Arrange - 使用一个35个字符的字符串
        user_message = "12345678901234567890123456789012345" * 2  # 70个字符
        ai_response = "AI回复"

        # Mock AI客户端抛出异常
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("AI服务不可用")

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert - 应该被截取到30个字符
        assert len(title) == 30
        assert title == "123456789012345678901234567890"

    def test_should_fallback_for_empty_message(self, title_generator):
        """
        测试4：用户输入为空时，应该返回默认标题
        """
        # Arrange
        user_message = ""
        ai_response = "AI回复"

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert
        assert title == "新对话"

    def test_should_truncate_long_titles(self, title_generator):
        """
        测试5：AI生成的标题过长时，应该截断到30字符
        """
        # Arrange
        user_message = "测试"
        ai_response = "测试回复"

        # Mock AI客户端返回超长标题
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是一个非常非常非常非常非常非常非常非常非常非常长的标题"
        mock_client.chat.completions.create.return_value = mock_response

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert - 标题应该被截断到30字符
        assert len(title) <= 30

    def test_should_remove_punctuation_from_title(self, title_generator):
        """
        测试6：应该从标题中移除标点符号
        """
        # Arrange
        user_message = "测试"
        ai_response = "测试回复"

        # Mock AI客户端返回带标点的标题
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"这是标题"，包含标点！'
        mock_client.chat.completions.create.return_value = mock_response

        title_generator.client = mock_client

        # Act
        import asyncio
        title = asyncio.run(title_generator.generate_title(user_message, ai_response))

        # Assert - 标点符号应该被移除
        assert '"' not in title
        assert '，' not in title
        assert '！' not in title
        assert title == "这是标题包含标点"
