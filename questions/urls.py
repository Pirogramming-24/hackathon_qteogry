from django.urls import path
from . import views


app_name = "questions"

urlpatterns = [
    # path('questions_read/<int:pk>', views.questions_read, name='questions_read'),
    path("understanding_check/<int:pk>/", views.understanding_check, name="understanding_check"),
    path("understanding_check/upload/", views.understanding_check_upload, name="understanding_check_upload"),
    path("understanding_check/respond/", views.understanding_check_respond, name="understanding_check_respond"),
    path('<int:session_id>/', views.question_main, name='question_main'),
    path('<int:session_id>/<int:question_id>/', views.question_detail, name='question_detail'),
    path("understanding_check/finish/<int:check_id>/", views.understanding_check_finish, name="understanding_check_finish"),
    # path('<int:session_id>/<int:question_id>/comments/create', views.comment_create,name='comment_create')
    path('like/<int:question_id>/', views.question_like, name='question_like'),
    path('status/<int:question_id>/', views.question_update_status, name='question_update_status'),
]