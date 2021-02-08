# @author: chengjie142039
# @file: redis_client.py
# @time: 2021/01/26
# @desc:

import redis
from django.conf import settings

rc = redis.Redis(**settings.REDIS_CONFIG)
