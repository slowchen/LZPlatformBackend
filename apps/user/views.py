from django.contrib.auth.hashers import check_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from LZPlatformBackend.core import code
from LZPlatformBackend.core.authentication import get_token
from LZPlatformBackend.core.exceptions import SerializerInvalidError
from LZPlatformBackend.core.permissions import AdminPermission
from LZPlatformBackend.core.response import APIResponse
from LZPlatformBackend.core.viewset import APIModelViewSet
# from apps.common.utils.operation_log import Log2Db
from apps.user import models
from apps.user.filters import UserFilter
from apps.user.serializers import UserSerializer, RoleSerializer, LoginSerializer, RegisterSerializer, \
    UserChangePwdSerializer, MenuSerializer
from utils.log import log


class LoginView(APIView):
    # 用户登录，获取 token
    """
    {"username": "admin", "password": "admin"}
    """

    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        request_data = request.data
        login_ser = LoginSerializer(data=request_data)
        if login_ser.is_valid():
            user = models.UserInfo.objects.filter(username=login_ser.data.get('username')).first()
            if user:
                if check_password(login_ser.data.get('password'), user.password):
                    token = get_token(user)
                    return APIResponse(data={'token': token})
                if not user.is_valid:
                    return APIResponse(msg='用户已被禁用', code=400)
            return APIResponse(msg='用户名或密码错误', code=400)
        log.error(f'参数错误, log_id:{request.log_id}', login_ser.errors)
        raise SerializerInvalidError(login_ser.errors)


class RegisterView(APIView):
    # 用户注册，注册成功后会直接获取到 token
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        request_data = request.data
        register_ser = RegisterSerializer(data=request_data)
        if register_ser.is_valid():
            user_ser = UserSerializer(data=request_data)
            if user_ser.is_valid():
                user = user_ser.save()
                token = get_token(user)
                data = user_ser.data
                data['token'] = token
                return APIResponse(data=data, msg='注册成功')
            raise SerializerInvalidError(user_ser.errors)
        raise SerializerInvalidError(register_ser.errors)


class UserInfo(APIView):
    # 当前登录用户，获取用户信息
    def post(self, request, *args, **kwargs):
        user_ser = UserSerializer(instance=request.user, many=False)
        return APIResponse(data=user_ser.data)


class UserChangePwd(APIView):
    """
    用户修改本人密码
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data
        change_pwd_ser = UserChangePwdSerializer(data=request_data)
        if change_pwd_ser.is_valid():
            if check_password(change_pwd_ser.data.get('old'), request.user.password):
                request.user.change_pwd(change_pwd_ser.data.get('new'))
                return APIResponse(msg='密码更新成功')
            return APIResponse(msg='旧密码错误')
        raise SerializerInvalidError(change_pwd_ser.errors)


class UserProfile(APIView):
    # 管理员获取某个用户信息
    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid')
        try:
            user = models.UserInfo.objects.get(uid=uid)
            user_ser = UserSerializer(instance=user)
            return APIResponse(data=user_ser.data)
        except models.UserInfo.DoesNotExist:
            log.error(f' uid:{uid}查询 user 为空')
            return APIResponse(msg='未查询到结果', code=code.OBJ_NOT_FOUND)
        except models.UserInfo.MultipleObjectsReturned:
            log.error(f' uid:{uid}查询 user 有多条')
            return APIResponse(msg='查询数据有多个，请检查数据', code=code.OBJ_FOUND_TOO_MANY)


class UserList(APIView):
    # 管理员获取所有用户信息
    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        try:
            user = models.UserInfo.objects.filter(**request.data).all()
            print(user)
            user_ser = UserSerializer(instance=user, many=True)
            return APIResponse(data=user_ser.data)
        except Exception as e:
            print(e)
            return APIResponse(msg='参数错误，请检查参数', code=code.PARAMS_INVALID)


class AddUser(APIView):
    """
    管理员新增用户
    """
    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        user_ser = UserSerializer(data=request.data)
        if user_ser.is_valid():
            user_ser.save()
            return APIResponse(data=user_ser.data)
        return APIResponse(data=user_ser.errors)


class UserInfoViewSet(APIModelViewSet):
    queryset = models.UserInfo.objects.all()  # 使用get_queryset函数，依赖queryset的值
    serializer_class = UserSerializer
    # pagination_class = GoodsPagination
    filter_backends = (DjangoFilterBackend,)  # 将过滤器后端添加到单个视图或视图集
    filterset_class = UserFilter


class ModifyUserProfile(APIView):
    """
    管理员修改用户资料
    """
    pass


class ModifyUserRole(APIView):
    """
    管理员修改用户角色
    """

    # permission_classes = [AdminPermission, ]

    def post(self, request, *args, **kwargs):
        request_data = request.data
        user = models.UserInfo.objects.get(id=request_data.get('user'))
        try:
            for role_obj in request_data.get('roles'):
                role_id = role_obj.get('role')
                role = models.Role.objects.get(id=role_id)
                status = role_obj.get('status')
                if role in user.all_roles():
                    user_role = models.UserRole.objects.filter(user=user, role=role).first()
                    user_role.status = status
                    user_role.save()
                    # Log2Db(user_role.id, Log2Db.ObjType.ROLE, Log2Db.OpType.UPDATE, request)
                else:
                    if status == 1:
                        user_role = models.UserRole.objects.create(user=user, role=role, status=status)
                        # Log2Db(user_role.id, Log2Db.ObjType.ROLE, Log2Db.OpType.INSERT, request)
            return APIResponse(msg='更新成功')
        except Exception as e:
            return APIResponse(msg=f'更新失败,{e}')


class RoleView(APIModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = RoleSerializer


"""
class SendRegisterSMSCodeView(APIView):
    authentication_classes = ()
    throttle_classes = (VerifyCodeThrottle,)

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        app_name = request.data.get('app_name')
        if is_phone(phone):
            send_register_sms(app_name, phone)
            return APIResponse(msg='发送成功')
        else:
            return APIResponse(msg=f'请检查手机号{phone}是否正确')
"""


class MenuAddView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        menu_ser = MenuSerializer(data=request.data)
        if menu_ser.is_valid():
            menu_ser.save()
            return APIResponse()
        else:
            return APIResponse(msg=menu_ser.errors)


class MenuOperateView(APIView):
    """
    菜单操作，增删改
    {
        'type': 1:新增 2:删除 3:编辑
        'id': null or int
        'name': '',
        'icon_class': '',
        'path': '',
        'parent': null or int
    }
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        op_type = request.data.get('type')
        data = request.data
        if op_type == 1:
            menu_ser = MenuSerializer(data=data)
            if menu_ser.is_valid():
                menu_ser.save()
                return APIResponse()
            else:
                return APIResponse(msg=menu_ser.errors)

        elif op_type == 2:
            obj = models.Menu.objects.filter(id=data.get('id')).first()
            obj.status = 0
            obj.save()
            return APIResponse(msg='删除成功')

        elif op_type == 3:
            obj = models.Menu.objects.filter(id=data.get('id')).first()
            if not obj:
                return APIResponse(msg='id 不存在', code=code.OBJ_NOT_FOUND)
            menu_ser = MenuSerializer(instance=obj, data=data)
            if menu_ser.is_valid():
                menu_ser.save()
                return APIResponse(msg='编辑成功')
            else:
                return APIResponse(msg=menu_ser.errors)

        else:
            return APIResponse(msg='非法输入', code=code.PARAMS_INVALID)


class MenuTreeView(APIView):
    """
    生成树形菜单，默认展示所有菜单，如果传入status=0则仅返回无效的菜单，，传入status=1则仅返回有效的菜单，其余则返回所有菜单
    {"status": 1} or {}
    """

    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        try:
            status = request.data.get('status')
            menus = models.Menu.objects.filter(parent__isnull=True).all()
            if status is not None:
                menus = menus.filter(status=status)
            ser = MenuSerializer(instance=menus, many=True, context={'status': status})
            return APIResponse(data=ser.data)
        except ValueError as e:
            return APIResponse(msg=e.args[0], code=code.PARAMS_INVALID)


class UserMenuListView(APIView):
    """
    查询当前登录用户的可用菜单列表
    """

    def post(self, request, *args, **kwargs):
        # 只查询有效状态的菜单
        ser = MenuSerializer(instance=request.user.menus(), many=True, context={'status': 1})
        import time
        time.sleep(1.1)
        return APIResponse(data=ser.data)
