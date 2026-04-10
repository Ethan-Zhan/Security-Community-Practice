from django.db import models
from feishu_auth.models import UserInfo


# 可能存在多设备bind情况 所以此处使用外键最合适
class BindInfo(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    device_id = models.PositiveIntegerField()
    logged_in = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'device_id', 'logged_in')
