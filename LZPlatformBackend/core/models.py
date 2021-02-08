from django.utils import timezone
from django.db import models


class BaseModel(models.Model):
    # create_by = models.ForeignKey(UserInfo, verbose_name='创建人', null=True,
    #                               on_delete=models.CASCADE, related_name='create_id')
    # update_by = models.ForeignKey(UserInfo, verbose_name='更新人', null=True,
    #                               on_delete=models.CASCADE, related_name='update_id')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
