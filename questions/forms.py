from django import forms
from .models import UnderstandingCheck, UnderstandingResponse

class UnderstandingForm(forms.ModelForm):
    class Meta:
        model = UnderstandingCheck
        fields = [
            'content'
        ]