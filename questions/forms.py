from django import forms
from .models import UnderstandingCheck, UnderstandingResponse
from .models import Question

class UnderstandingForm(forms.ModelForm):
    class Meta:
        model = UnderstandingCheck
        fields = [
            'content'
        ]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'title', 'content', 'image']
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'input-category_ny', 
                'placeholder': '질문 종류 선택'
            }),
            'title': forms.TextInput(attrs={
                'class': 'input-title_ny', 
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'input-content_ny', 
                'rows': 10, 
                'placeholder': '질문 내용을 구체적으로 작성해주세요.'
            }),
            'image': forms.FileInput(attrs={
                'class': 'input-image_ny'
            }),
            # 'timing': forms.RadioSelect(attrs={
            #     'class': 'input-timing_ny'
            # }),
        }
        
        labels = {
            'category': '질문 종류',
            'title': '제목',
            'content': '내용',
            'image': '이미지 첨부',
            # 'timing': '답변 희망 시간',
        }
