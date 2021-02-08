from django.conf import settings
from rest_framework.views import exception_handler

from ..core import code
from ..core.response import APIResponse

log = settings.LOGGER


def custom_exception_handler(exc, context):
    # path = context['request'].stream.path
    # view = context['view']
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code == 400:
            # 400包括ValidationError和ParseError
            if exc.default_code == 'invalid':
                # msg = list(exc.detail.values())[0][0]
                return APIResponse(msg='输入不合法', code=code.PARAMS_INVALID, error=exc.detail)

            if exc.default_code == 'parse_error':
                return APIResponse(msg=exc.detail, code=code.PARAMS_INVALID)

            # if exc.default_code == 'serializer_invalid':
            #     msg = list(exc.detail.values())[0][0]
            #     return APIResponse(msg=msg, code=code.SERIALIZER_INVALID)

        if response.status_code == 401:
            return APIResponse(msg=exc.detail, code=code.AUTH_FAILED)

        if response.status_code == 403:
            return APIResponse(msg=exc.detail, code=code.PERMISSION_FAILED)

        if response.status_code == 404:
            return APIResponse(msg='请求路径不存在', code=code.PATH_NOT_FOUND)

        if response.status_code == 405:
            return APIResponse(msg=exc.detail, code=code.METHOD_NOT_ALLOWED)

        if response.status_code == 429:
            return APIResponse(msg=f'请求次数超过限制，请在{exc.wait}秒后重新请求', code=code.TOO_MANY_REQUESTS)

        if response.status_code == 599:
            msg = list(exc.detail.values())[0][0]
            return APIResponse(msg=msg, code=code.SERIALIZER_INVALID)

        if response.status_code == 598:
            return APIResponse(msg='未查询到结果', code=code.OBJ_NOT_FOUND)

        if response.status_code == 560:
            return APIResponse(msg=exc.detail, code=code.DB_SAVE_ERROR)

    else:
        view = context['view']
        error = '服务器开小差咯😭'
        return APIResponse(msg=f'{error}[{view}]', code=code.INTERNAL_SERVER_ERROR)
