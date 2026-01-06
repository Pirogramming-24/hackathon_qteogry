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
    # path('<int:session_id>/<int:question_id>/comments/create', views.comment_create,name='comment_create')
https://github.com/Pirogramming-24/hackathon_qtegory/pull/20/conflict?name=questions%252Fviews.py&ancestor_oid=6a5f60b6828af18a168f4024e83bded43b4fb5f6&base_oid=5405aec8ff7df97913a64753c58879dab92fb363&head_oid=63470c24fd0c999610c0b1d4b430b11d84d407a9    path('like/<int:question_id>/', views.question_like, name='question_like'),
    path('status/<int:question_id>/', views.question_update_status, name='question_update_status'),
]