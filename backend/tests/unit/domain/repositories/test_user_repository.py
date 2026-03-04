"""
UserRepository接口测试
"""
import pytest
from unittest.mock import Mock
from src.domain.repositories.user import UserRepository
from src.domain.entities.user import User


class TestUserRepository:
    """测试UserRepository接口定义"""

    def test_user_repository_is_abstract(self):
        """测试UserRepository是抽象类，无法直接实例化"""
        with pytest.raises(TypeError):
            UserRepository()

    def test_user_repository_has_required_methods(self):
        """测试UserRepository定义了所有必需的抽象方法"""
        # 检查所有抽象方法是否存在
        abstract_methods = UserRepository.__abstractmethods__
        expected_methods = {
            'get_by_id',
            'get_by_username',
            'get_by_email',
            'create',
            'update',
            'delete',
            'list_all'
        }
        assert abstract_methods == expected_methods

    def test_concrete_implementation_can_be_created(self):
        """测试可以创建具体的实现类"""
        class ConcreteUserRepository(UserRepository):
            """具体的UserRepository实现"""

            async def get_by_id(self, user_id: str):
                return None

            async def get_by_username(self, username: str):
                return None

            async def get_by_email(self, email: str):
                return None

            async def create(self, user: User):
                return user

            async def update(self, user: User):
                return user

            async def delete(self, user_id: str):
                pass

            async def list_all(self, skip: int = 0, limit: int = 100):
                return []

        # 应该能够实例化具体实现
        repo = ConcreteUserRepository()
        assert isinstance(repo, UserRepository)

    @pytest.mark.asyncio
    async def test_user_repository_method_signatures(self):
        """测试UserRepository方法签名"""
        class ConcreteUserRepository(UserRepository):
            """具体的UserRepository实现"""

            async def get_by_id(self, user_id: str):
                return Mock(spec=User)

            async def get_by_username(self, username: str):
                return Mock(spec=User)

            async def get_by_email(self, email: str):
                return Mock(spec=User)

            async def create(self, user: User):
                return user

            async def update(self, user: User):
                return user

            async def delete(self, user_id: str):
                pass

            async def list_all(self, skip: int = 0, limit: int = 100):
                return []

        repo = ConcreteUserRepository()

        # 测试方法可以被调用
        result = await repo.get_by_id("user123")
        assert result is not None

        result = await repo.get_by_username("testuser")
        assert result is not None

        result = await repo.get_by_email("test@example.com")
        assert result is not None

        user = Mock(spec=User)
        result = await repo.create(user)
        assert result == user

        result = await repo.update(user)
        assert result == user

        await repo.delete("user123")  # 不应抛出异常

        result = await repo.list_all(skip=0, limit=10)
        assert isinstance(result, list)
