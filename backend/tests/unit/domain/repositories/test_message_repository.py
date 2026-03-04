"""
MessageRepository接口测试
"""
import pytest
from unittest.mock import Mock
from src.domain.repositories.message import MessageRepository
from src.domain.entities.message import Message


class TestMessageRepository:
    """测试MessageRepository接口定义"""

    def test_message_repository_is_abstract(self):
        """测试MessageRepository是抽象类，无法直接实例化"""
        with pytest.raises(TypeError):
            MessageRepository()

    def test_message_repository_has_required_methods(self):
        """测试MessageRepository定义了所有必需的抽象方法"""
        abstract_methods = MessageRepository.__abstractmethods__
        expected_methods = {
            'get_by_id',
            'get_by_session_id',
            'create',
            'create_batch',
            'delete',
            'delete_by_session_id'
        }
        assert abstract_methods == expected_methods

    def test_concrete_implementation_can_be_created(self):
        """测试可以创建具体的实现类"""
        class ConcreteMessageRepository(MessageRepository):
            """具体的MessageRepository实现"""

            async def get_by_id(self, message_id: str):
                return None

            async def get_by_session_id(
                self,
                session_id: str,
                skip: int = 0,
                limit: int = 100
            ):
                return []

            async def create(self, message: Message):
                return message

            async def create_batch(self, messages: list):
                return messages

            async def delete(self, message_id: str):
                pass

            async def delete_by_session_id(self, session_id: str):
                pass

        # 应该能够实例化具体实现
        repo = ConcreteMessageRepository()
        assert isinstance(repo, MessageRepository)

    @pytest.mark.asyncio
    async def test_message_repository_method_signatures(self):
        """测试MessageRepository方法签名"""
        class ConcreteMessageRepository(MessageRepository):
            """具体的MessageRepository实现"""

            async def get_by_id(self, message_id: str):
                return Mock(spec=Message)

            async def get_by_session_id(
                self,
                session_id: str,
                skip: int = 0,
                limit: int = 100
            ):
                return []

            async def create(self, message: Message):
                return message

            async def create_batch(self, messages: list):
                return messages

            async def delete(self, message_id: str):
                pass

            async def delete_by_session_id(self, session_id: str):
                pass

        repo = ConcreteMessageRepository()

        # 测试方法可以被调用
        result = await repo.get_by_id("msg123")
        assert result is not None

        result = await repo.get_by_session_id("session123", skip=0, limit=10)
        assert isinstance(result, list)

        message = Mock(spec=Message)
        result = await repo.create(message)
        assert result == message

        messages = [Mock(spec=Message), Mock(spec=Message)]
        result = await repo.create_batch(messages)
        assert result == messages

        await repo.delete("msg123")  # 不应抛出异常
        await repo.delete_by_session_id("session123")  # 不应抛出异常
