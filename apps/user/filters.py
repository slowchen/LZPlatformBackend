from django_filters import rest_framework as filters

from .models import UserInfo


class UserFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='contains')  # 包含关系，模糊匹配
    email = filters.CharFilter(field_name='email')
    real_name = filters.CharFilter(field_name="real_name")
    status = filters.NumberFilter(field_name="status")
    # role = filters.NumberFilter(field_name="role")

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'real_name', 'status', 'role']
