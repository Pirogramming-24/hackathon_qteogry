
from django.urls import path
from .views import *

app_name = "live_sessions"

urlpatterns = [
    # prefix = sessions/
    # 세션 목록 (메인)
    path("", SessionListView.as_view(), name="session_list"),
    # 기수 생성
    path("generations/new/", GenerationCreateView.as_view(), name="generation_create"),
    # 세션 생성
    path("new/", LiveSessionCreateView.as_view(), name="session_create"),
    
]