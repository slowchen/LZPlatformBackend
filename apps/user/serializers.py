from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.user.models import UserInfo, Role, UserRole, Menu


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, error_messages={'required': 'username必填', 'blank': 'username不能为空'})
    password = serializers.CharField(required=True, error_messages={'required': 'password必填', 'blank': 'password不能为空'})

    class Meta:
        fields = ('username', 'password',)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, required=True,
                                     error_messages={'required': 'username必填', 'blank': 'username不能为空'})
    password = serializers.CharField(max_length=256, min_length=8, required=True,
                                     error_messages={'required': 'password必填', 'blank': 'password不能为空',
                                                     'min_length': '密码最少8位'})
    confirm_password = serializers.CharField(required=True,
                                             error_messages={'required': 'password必填', 'blank': 'confirm_password不能为空'})
    real_name = serializers.CharField(max_length=10, required=True,
                                      error_messages={'required': 'real_name必填', 'blank': 'real_name不能为空'})
    phone = serializers.CharField(max_length=11, required=True, min_length=11,
                                  error_messages={'required': 'phone必填', 'blank': 'phone不能为空'})
    employee_code = serializers.CharField(max_length=7, required=True,
                                          error_messages={'required': 'employee_code必填', 'blank': 'employee_code不能为空'})
    email = serializers.EmailField(required=True,
                                   error_messages={'required': 'email必填', 'blank': 'email不能为空'})

    class Meta:
        fields = ('username', 'password', 'confirm_password', 'real_name', 'email', 'phone', 'employee_code')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('两次密码不一致')
        return attrs


class UserChangePwdSerializer(serializers.Serializer):
    old = serializers.CharField(max_length=256, min_length=8, required=True,
                                error_messages={'required': '旧密码必填', 'blank': '旧密码不能为空',
                                                'min_length': '密码最少8位'})
    new = serializers.CharField(max_length=256, min_length=8, required=True,
                                error_messages={'required': '新密码必填', 'blank': '新密码不能为空',
                                                'min_length': '密码最少8位'})
    confirm = serializers.CharField(max_length=256, min_length=8, required=True,
                                    error_messages={'required': '新密码必填', 'blank': '新密码不能为空',
                                                    'min_length': '密码最少8位'})

    class Meta:
        fields = ('old', 'new', 'confirm')

    def validate(self, attrs):
        if attrs.get('new') != attrs.get('confirm'):
            raise serializers.ValidationError('两次密码不一致')
        return attrs


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ('uid', 'username', 'password', 'phone', 'employee_code', 'real_name', 'email', 'roles', 'status')
        extra_kwargs = {
            'password': {'write_only': True},
            'status': {'read_only': True},
            'username': {
                'validators': [UniqueValidator(queryset=UserInfo.objects.all(), message='用户已经存在')]
            }
        }

    def get_roles(self, obj):
        roles = obj.valid_roles()
        role_ser = RoleSerializer(instance=roles, many=True)
        return role_ser.data


class ModifyUserProfileSerializer(serializers.ModelSerializer):
    pass


class ModifyUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('user', 'role', 'status')


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单
    """
    sub = serializers.SerializerMethodField()
    parent = serializers.IntegerField(source='parent_id', allow_null=True)

    class Meta:
        model = Menu
        fields = ('id', 'name', 'icon_class', 'path', 'tier', 'parent', 'sub', 'status')
        depth = 2
        extra_kwargs = {
            'sub': {'read_only': True}
        }

    def get_sub(self, obj):
        """
        获取子菜单
        :param obj:
        :return:
        """
        status = self.context['status']
        sub_menus = Menu.objects.filter(parent=obj).all()
        if status is not None:
            sub_menus = sub_menus.filter(status=status)
        # 注意此处需要使用context传递request，many=True，会遍历赋值，不传递的话第二次遍历的时候拿不到 request 对象
        sub_menus_ser = MenuSerializer(instance=sub_menus, many=True, context={'status': status})
        return sub_menus_ser.data


class RoleSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'role_name', 'role_code', 'role_desc', 'menus')
        extra_kwargs = {
            'role_code': {
                'validators': [UniqueValidator(queryset=Role.objects.all(), message='角色代码已经存在')],
            }
        }

    def validate_role_code(self, value):
        if value.upper() != value:
            raise serializers.ValidationError('角色代码必须全部大写')
        return value

    def get_menus(self, obj):
        # 'status': 1 只查询有效的菜单
        ser = MenuSerializer(instance=obj.menus(), many=True, context={'status': 1})
        return ser.data
