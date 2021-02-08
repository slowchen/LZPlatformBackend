from rest_framework.throttling import SimpleRateThrottle


class VerifyCodeThrottle(SimpleRateThrottle):
    """
    验证码频率限制，每个 ip 每分钟10次
    """
    scope = 'verify_code'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class GlobalThrottle(SimpleRateThrottle):
    """
    全局限制，每个 ip 每分钟100次
    """
    scope = 'global'

    def get_cache_key(self, request, view):
        return self.get_ident(request)
