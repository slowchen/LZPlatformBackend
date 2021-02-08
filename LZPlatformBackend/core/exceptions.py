from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import *


class ObjExisted(Exception):
    pass


class SerializerInvalidError(APIException):
    status_code = 599
    default_detail = _('Serializer invalid.')
    default_code = 'serializer_invalid'


class ValidationError(ValidationError):
    pass


class ParseError(ParseError):
    pass


class AuthenticationFailed(AuthenticationFailed):
    pass


class NotAuthenticated(NotAuthenticated):
    pass


class PermissionDenied(PermissionDenied):
    pass


class NotFound(NotFound):
    pass


class MethodNotAllowed(MethodNotAllowed):
    pass


class NotAcceptable(NotAcceptable):
    pass


class UnsupportedMediaType(UnsupportedMediaType):
    pass


class Throttled(Throttled):
    pass


class ObjDoesNotExistError(APIException):
    status_code = 598
    default_detail = _('Obj not exist.')
    default_code = 'obj_not_exist'


class DBSaveError(APIException):
    status_code = 560
    default_detail = _('Database save error.')
    default_code = 'db_save_error'
