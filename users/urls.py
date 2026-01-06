from django.urls import path
from . import views

app_name = 'users'  # 네임스페이스 설정 (충돌 방지)

urlpatterns = [
    # 주소: 127.0.0.1:8000/users/login/
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]