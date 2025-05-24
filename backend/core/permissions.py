# core/permissions.py
from rest_framework.permissions import BasePermission


# 注册用户权限
class IsActive(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active
    

# 渔民权限
class IsFisher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'fisher')


# 管理员权限
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'