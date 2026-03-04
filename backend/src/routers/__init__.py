# -*- coding: utf-8 -*-
"""路由模块

将 main.py 中的路由按功能拆分到不同模块中，提高代码可维护性。

迁移状态：
- ✅ auth_router -> src/interfaces/routers/auth/
- ✅ sessions_router -> src/interfaces/routers/sessions/
- ✅ tools_router -> src/interfaces/routers/tools/（2026-03-01）
- ✅ users_router -> src/interfaces/routers/users/（2026-03-02）
- ✅ admin_tools_router -> src/interfaces/routers/admin/tools/（2026-03-02）
- ✅ works_router -> src/interfaces/routers/works/（2026-03-02）
- ✅ courses_router -> src/interfaces/routers/courses/（2026-03-02）
- ✅ common_router -> src/interfaces/routers/common/（2026-03-02）
"""

# from .users import router as users_router  # 已迁移到 interfaces 层（2026-03-02）
# from .tools import router as tools_router  # 已迁移到 interfaces 层（2026-03-01）
# from .sessions import router as sessions_router  # 已迁移到 interfaces 层
# from .admin_tools import router as admin_tools_router  # 已迁移到 interfaces 层（2026-03-02）
# from .works import router as works_router  # 已迁移到 interfaces 层（2026-03-02）
# from .courses import router as courses_router  # 已迁移到 interfaces 层（2026-03-02）
# from .common import router as common_router  # 已迁移到 interfaces 层（2026-03-02）

__all__ = [
    # "users_router",  # 已迁移到 interfaces 层（2026-03-02）
    # "tools_router",  # 已迁移到 interfaces 层（2026-03-01）
    # "sessions_router",  # 已迁移到 interfaces 层
    # "admin_tools_router",  # 已迁移到 interfaces 层（2026-03-02）
    # "works_router",  # 已迁移到 interfaces 层（2026-03-02）
    # "courses_router",  # 已迁移到 interfaces 层（2026-03-02）
    # "common_router",  # 已迁移到 interfaces 层（2026-03-02）
]
