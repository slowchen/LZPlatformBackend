from rest_framework.response import Response
from rest_framework.serializers import Serializer, ListSerializer

from ..core import code as resp_code
from utils.utils import now


class APIResponse(Response):
    """
    自定义response类，对response body、header格式化
    """

    def __init__(self, data=None, status=None, headers=None,
                 exception=False, code=resp_code.REQUEST_SUCCESS, msg='success', **kwargs):

        if isinstance(data, (Serializer, ListSerializer)):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)
        else:
            return_data = data
        result = {
            'code': code,
            'msg': msg,
            'data': return_data,
            'timestamp': now().timestamp
        }
        if kwargs:
            result.update(kwargs)
        super().__init__(data=result, status=status, headers=headers, exception=exception)
