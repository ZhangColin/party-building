# -*- coding: utf-8 -*-
"""用户管理路由模块

此模块提供用户管理相关的API路由，包括：
- 用户列表查询（分页、筛选）
- 创建用户
- 获取用户详情
- 更新用户信息
- 删除用户
- 重置用户密码

所有端点都需要管理员权限。
"""
from src.interfaces.routers.users.users import router

__all__ = ["router"]
