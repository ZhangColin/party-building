"""
SessionRepository接口测试
"""
import pytest
from unittest.mock import Mock
from src.domain.repositories.session import SessionRepository
from src.domain.entities.session import Session


class TestSessionRepository:
    """测试SessionRepository接口定义"""

    def test_session_repository_is_abstract(self):
        """测试SessionRepository是抽象类，无法直接实例化"""
        with pytest.raises(TypeError):
            SessionRepository()

    def test_session_repository_has_required_methods(self):
        """测试SessionRepository定义了所有必需的抽象方法"""
        abstract_methods = SessionRepository.__abstractmethods__
        expected_methods = {
            'get_by_id',
            'get_by_user_id',
            'create',
            'update',
            'delete'
        }
        assert abstract_methods == expected_methods

    def test_concrete_implementation_can_be_created(self):
        """测试可以创建具体的实现类"""
        class ConcreteSessionRepository(SessionRepository):
            """具体的SessionRepository实现"""

            async def get_by_id(self, session_id: str):
                return None

            async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100):
                return []

            async def create(self, session: Session):
                return session

            async def update(self, session: Session):
                return session

            async def delete(self, session_id: str):
                pass

        # 应该能够实例化具体实现
        repo = ConcreteSessionRepository()
        assert isinstance(repo, SessionRepository)

    @pytest.mark.asyncio
    async def test_session_repository_method_signatures(self):
        """测试SessionRepository方法签名"""
        class ConcreteSessionRepository(SessionRepository):
            """具体的SessionRepository实现"""

            async def get_by_id(self, session_id: str):
                return Mock(spec=Session)

            async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100):
                return []

            async def create(self, session: Session):
                return session

            async def update(self, session: Session):
                return session

            async def delete(self, session_id: str):
                pass

        repo = ConcreteSessionRepository()

        # 测试方法可以被调用
        result = await repo.get_by_id("session123")
        assert result is not None

        result = await repo.get_by_user_id("user123", skip=0, limit=10)
        assert isinstance(result, list)

        session = Mock(spec=Session)
        result = await repo.create(session)
        assert result == session

        result = await repo.update(session)
        assert result == session

        await repo.delete("session123")  # 不应抛出异常
