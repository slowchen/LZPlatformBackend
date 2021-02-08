import random
import string
import time
import uuid

import arrow
import validators


def now():
    """
    获取当前时间，datetime 格式
    :return: datetime
    """
    return arrow.now()


def timestamp(times):
    """
    获取时间戳.10位 秒级
    :param times:
    :return: timestamp
    """
    return times.timestamp


def gen_time_by_interval(**kwargs):
    """
    以当前时间为基准，根据时间间隔，生成一个时间
    :param kwargs:
    eg:
        weeks=1
        days=-1
        hours=6
        months=-6
        years=3
    可以组合使用
    :return: datetime
    """
    return arrow.now().shift(**kwargs)


def gen_uuid():
    return str(uuid.uuid1()).replace('-', '')


def gen_id(size=16, chars=string.ascii_lowercase + string.digits + str(int(time.time()))):
    return ''.join(random.choice(chars) for _ in range(size))


def gen_sms_code(size=6, chars=string.digits):
    """生成短信验证码"""
    return ''.join(random.choice(chars) for _ in range(size))


def is_email(value):
    return validators.email(value)


def filter_model(model, **kwargs):
    r = model.objects.filter(**kwargs)
    return r


def get_nonce():
    """
    生成32位随机码
    :return:
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, 32))


if __name__ == '__main__':
    print(gen_sms_code())
