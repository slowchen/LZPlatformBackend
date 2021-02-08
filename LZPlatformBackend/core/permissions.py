from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.has_one_admin:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # 判断是否有对象操作权限，判断条件为对象创建人或者具有管理员权限
        if request.user == obj.create_by:
            return True
        if request.user.has_one_admin:
            return True
        return False
