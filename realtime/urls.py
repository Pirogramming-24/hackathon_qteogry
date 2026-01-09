from django.urls import path
from . import views

app_name = "realtime"

urlpatterns = [
    path(
        "sse/sessions/<str:session_code>/",
        views.session_event_stream,
        name="session_sse",
    ),
]
