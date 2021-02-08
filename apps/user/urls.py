# @author: chengjie142039
# @email: 644209001@qq.com
# @file: urls.py
# @time: 2021/02/08
# @desc: app.user.urls


from django.urls import path

from apps.user import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view()),
    # path('send-register-code', views.SendRegisterSMSCodeView.as_view()),
    path('change-pwd', views.UserChangePwd.as_view()),
    path('info', views.UserInfo.as_view()),
    path('profile', views.UserProfile.as_view()),
    path('add', views.AddUser.as_view()),
    path('list', views.UserList.as_view()),
    path('modify-role', views.ModifyUserRole.as_view()),
    path('role', views.RoleView.as_view({'get': 'list', 'post': 'create'})),
    path('all-user', views.UserInfoViewSet.as_view({'get': 'list'})),
    path('menus', views.MenuAddView.as_view()),
    path('menu-operate', views.MenuOperateView.as_view()),
    path('menu-tree', views.MenuTreeView.as_view()),
    path('menu-list', views.UserMenuListView.as_view()),
]
