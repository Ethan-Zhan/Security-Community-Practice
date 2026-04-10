from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.db import models


class UserInfoManager(BaseUserManager):
    def create_user(self, open_id, name, en_name, avatar_big, avatar_middle, avatar_thumb, avatar_url, tenant_key,
                    union_id, email=None, password=None, **extra_fields):
        if not open_id:
            raise ValueError('必须提供open_id')
        if not name:
            raise ValueError('必须提供用户名称')

        user = self.model(
            open_id=open_id,
            name=name,
            en_name=en_name,
            avatar_big=avatar_big,
            avatar_middle=avatar_middle,
            avatar_thumb=avatar_thumb,
            avatar_url=avatar_url,
            tenant_key=tenant_key,
            union_id=union_id,
            email=email,
            **extra_fields
        )

        # 设置不可用密码或设置默认密码
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user


class UserInfo(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=False, verbose_name="名称")
    en_name = models.CharField(max_length=255, blank=False, verbose_name="英文名称")
    email = models.EmailField(null=True, blank=True)
    avatar_big = models.URLField(blank=False, verbose_name="头像大")
    avatar_middle = models.URLField(blank=False, verbose_name="头像中")
    avatar_thumb = models.URLField(blank=False, verbose_name="头像小")
    avatar_url = models.URLField(blank=False, verbose_name="头像url")
    open_id = models.CharField(max_length=255, unique=True, blank=False, verbose_name="应用ID")
    tenant_key = models.CharField(max_length=255, blank=False, verbose_name="租户key")
    union_id = models.CharField(max_length=255, blank=False, verbose_name="联合ID")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserInfoManager()

    USERNAME_FIELD = 'open_id'  # 使用open_id作为登录标识
    REQUIRED_FIELDS = ['name', 'en_name', 'avatar_big', 'avatar_middle', 'avatar_thumb', 'avatar_url', 'tenant_key',
                       'union_id']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
