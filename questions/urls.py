from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
	path('questions_read/<int:pk>', views.questions_read, name='questions_read'),
    # 예: /questions/1/ -> 1번 세션의 질문방
    path('<int:session_id>/', views.question_main, name='question_main'),
]