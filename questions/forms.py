from django import forms
from .models import UnderstandingCheck, UnderstandingResponse,Question, Comment


class UnderstandingForm(forms.ModelForm):
    class Meta:
        model = UnderstandingCheck
        # 👇 target_response_count 필드를 추가했습니다.
        fields = ['content', 'target_response_count']
        
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'input-content_ny', 
                'placeholder': 'DB 개론 실습 1'
            }),
            # 👇 목표 인원 입력창 (최소 1명)
            'target_response_count': forms.NumberInput(attrs={
                'class': 'input-count_ny',
                'placeholder': '목표 인원 (명)',
                'min': 1,
                'value': 20  # 기본값
            })
        }
        labels = {
            'content': '질문 내용',
            'target_response_count': '목표 응답 인원',
        }


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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets= {
            'content' : forms.TextInput(attrs={
                'class' : 'input-content_ny',
                'rows' : 3,
                'placeholder' : '댓글 작성',
            })
        }
        labels = {
            'content': '댓글 내용',
        }