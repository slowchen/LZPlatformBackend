import jwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from LZPlatformBackend import settings
from utils.utils import now, timestamp, gen_time_by_interval
from apps.user.models import UserInfo


def get_token(user, **kwargs):
    """
    生成token，过期时间6hours
    :param user: user obj
    :param kwargs:
    :return:
    """
    payload = {
        'iat': timestamp(now()),
        'exp': gen_time_by_interval(**settings.JWT.get('EXP_TIMEDELTA')).timestamp,
        'sub': settings.JWT.get('SUBJECT'),
        'uid': user.uid
    }
    payload.update(kwargs)
    try:
        token = jwt.encode(payload, key=settings.JWT.get('KEY'),
                           algorithm=settings.JWT.get('ALGORITHM', 'HS256')
                           )
        return token
    except jwt.exceptions.PyJWTError:
        raise jwt.exceptions.PyJWTError('token生成失败,请检查参数')


def authenticate_token(jwt_token):
    """
    解析token，获取user
    :param jwt_token:
    :return:
    """
    try:
        payload = jwt.decode(jwt_token,
                             key=settings.JWT.get('KEY'),
                             algorithms=[settings.JWT.get('ALGORITHM')]
                             )
        sub = payload.get('sub')
        if sub != settings.JWT.get('SUBJECT'):
            raise exceptions.AuthenticationFailed(f'无效的token {jwt_token}，请重新登录')
        uid = payload.get('uid')
        user = UserInfo.objects.get(uid=uid)
        return user
    except Exception:
        raise jwt.exceptions.DecodeError(f'token {jwt_token} 解析失败,请检查参数')


class JWTAuthentication(BaseAuthentication):
    """
    jwt认证
    """

    def authenticate(self, request):
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise exceptions.AuthenticationFailed('无效的token，请重新登录')
        auth = authorization.split()
        if not auth or auth[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('无效的token，请重新登录')

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('无效的token，请重新登录')
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed('无效的token，请重新登录')

        try:
            token = auth[1]
            user = authenticate_token(token)
            return user, token
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed('无效的token，请重新登录')
        except jwt.exceptions.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('token已过期，请重新登录')

    def authenticate_header(self, request):
        pass


if __name__ == '__main__':
    pass
