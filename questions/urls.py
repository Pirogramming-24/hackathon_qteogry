from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
	    path('questions_read/<int:pk>', views.questions_read, name='questions_read'),
]