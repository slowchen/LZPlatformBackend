from django.db import models

# Create your models here.

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

from LZPlatformBackend.core.exceptions import DBSaveError
from LZPlatformBackend.core.models import BaseModel
from utils.utils import gen_id


class UserInfo(BaseModel):
    # 用户表
    uid = models.CharField(max_length=32, unique=True, default=gen_id)
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=256, blank=False, null=False)
    email = models.EmailField(null=True, blank=True)
    real_name = models.CharField(max_length=10, null=True, blank=True)
    status = models.IntegerField(default=1)

    # role = models.ManyToManyField(Role)

    class Meta:
        db_table = 'user'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.username}'

    def save(self, *args, **kwargs):
        """
        入库时，密码保存为hash
        :param args:
        :param kwargs:
        :return:
        """
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def change_pwd(self, pwd):
        self.password = make_password(pwd)
        self.save()

    @property
    def is_valid(self):
        if self.status == 1:
            return True
        else:
            return False

    @property
    def has_admin(self):
        """
        判断是否有ADMIN角色
        :return:
        """
        admin_role = Role.objects.filter(role_code='ADMIN').first()
        if admin_role and admin_role in self.valid_roles():
            return True
        return False

    @property
    def has_super_admin(self):
        """
        判断是否有SUPERADMIN角色
        :return:
        """
        super_admin_role = Role.objects.filter(role_code='SUPERADMIN').first()
        if super_admin_role and super_admin_role in self.valid_roles():
            return True
        return False

    @property
    def has_all_admin(self):
        """
        判断是否同时有ADMIN和SUPERADMIN角色
        :return:
        """
        if self.has_admin and self.has_super_admin:
            return True
        return False

    @property
    def has_one_admin(self):
        """
        判断是否有ADMIN或SUPERADMIN其中任意一个角色
        :return:
        """
        if self.has_admin or self.has_super_admin:
            return True
        return False

    def valid_roles(self):
        """
        查询当前用户有效角色列表
        :return:
        """
        user_role = UserRole.objects.filter(user=self, status=1).select_related('role').all()
        return [i.role for i in user_role]

    def all_roles(self):
        """
        查询当前用户所有有效角色列表
        :return:
        """
        user_role = UserRole.objects.filter(user=self).select_related('role').all()
        return [i.role for i in user_role]

    def menus(self):
        """
        获取user的所有菜单，去重
        :return:
        """
        role_menus = [role.menus() for role in self.valid_roles()]
        menus = []
        for role_menu in role_menus:
            for menu in role_menu:
                menus.append(menu)
        return list(set(menus))


class Role(BaseModel):
    # 角色表
    role_code = models.CharField('角色代码', max_length=10, unique=True, null=False)
    role_name = models.CharField('角色名称', max_length=10, unique=True, null=False)
    role_desc = models.CharField('角色描述', max_length=50, null=False)
    status = models.IntegerField('状态', default=1)
    create_by = models.ForeignKey(UserInfo, related_name='role_create', verbose_name='创建人', null=True,
                                  on_delete=models.CASCADE, db_column='create_id')
    update_by = models.ForeignKey(UserInfo, related_name='role_update', verbose_name='更新人', null=True,
                                  on_delete=models.CASCADE, db_column='update_id')

    class Meta:
        db_table = 'role'
        verbose_name = '角色管理'
        verbose_name_plural = verbose_name
        ordering = ('id',)

    def __str__(self):
        return self.role_code

    def all_user(self):
        """
        获取拥有当前角色的所有用户
        :return:
        """
        user_role_list = UserRole.objects.filter(role=self).select_related('user').all()
        return [i.user for i in user_role_list]

    def menus(self):
        """
        获取当前角色的所有有效菜单
        :return:
        """
        menus = Menu.objects.filter(menu__role=self, status=1).all()
        if len(menus) > 0:
            return menus
        return []


class UserRole(BaseModel):
    # 用户角色表
    user = models.ForeignKey('UserInfo', related_name='role', null=False, default=0, on_delete=models.SET_DEFAULT,
                             db_column='user_id')
    role = models.ForeignKey('Role', related_name='user', null=True, on_delete=models.SET_NULL,
                             db_column='role_id')
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'user_role'
        verbose_name = '用户角色关联表'
        verbose_name_plural = verbose_name
        ordering = ('id',)
        unique_together = [
            ('user', 'role')
        ]

    # def save(self, *args, **kwargs):
    #     self.create_time = now()
    #     self.update_time = now()
    #     super().save(*args, **kwargs)


class Menu(BaseModel):
    name = models.CharField(max_length=10, null=False)
    icon_class = models.CharField(max_length=100, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=1)
    parent = models.ForeignKey('self', related_name='pid', verbose_name='父级菜单', null=True,
                               on_delete=models.CASCADE)
    tier = models.IntegerField(default=None, verbose_name='菜单层级')

    class Meta:
        db_table = 'menu'
        verbose_name = '菜单管理'
        verbose_name_plural = verbose_name
        ordering = ('id',)
        unique_together = [
            ('name', 'path', 'parent')
        ]

    def __str__(self):
        return f'{self.id}-{self.name}'

    def set_tier(self):
        """
        设置菜单层级
        :return:
        """
        if self.parent is None:
            return 1
        else:
            return self.parent.tier + 1

    def save(self, *args, **kwargs):
        if not self.tier:
            self.tier = self.set_tier()
        if self.tier > settings.MENU_TIER_MAX:
            raise DBSaveError('菜单层级过多，请控制在3层以内')
        super(Menu, self).save(*args, **kwargs)


class RoleMenu(BaseModel):
    menu = models.ForeignKey('Menu', related_name='menu', null=False, default=0, on_delete=models.SET_DEFAULT,
                             db_column='menu_id')
    role = models.ForeignKey('Role', related_name='role', null=False, default=0, on_delete=models.SET_DEFAULT,
                             db_column='role_id')
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'role_menu'
