# live_sessions/forms.py
from django import forms
from .models import Generation, LiveSession


class GenerationForm(forms.ModelForm):
    class Meta:
        model = Generation
        fields = ["name"]
        labels = {
            "name": "기수 이름",
        }


class LiveSessionForm(forms.ModelForm):
    class Meta:
        model = LiveSession
        fields = ["generation", "title", "start_at", "end_at"]
        labels = {
            "generation": "기수",
            "title": "세션 제목",
            "start_at": "시작 일시",
            "end_at": "종료 일시",
        }
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
