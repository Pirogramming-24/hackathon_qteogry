from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.ModelForm):
    """
    하나로 합친 완전체 회원가입 폼
    """
    
    # 1. 아이디 필드
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={
            'placeholder': '아이디를 입력하세요',
        }),
    )
    
    # 2. 비밀번호 필드 (기존에 누락되었던 부분 복구)
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 입력하세요 (최소 4자리)',
            'autocomplete': 'new-password'  # 브라우저 자동완성 꼬임 방지
        }),
        help_text='최소 4자리 이상 입력해주세요.'
    )
    
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 다시 입력하세요',
            'autocomplete': 'new-password'
        }),
    )

    # 3. 역할 선택 필드 (라디오)
    ROLE_CHOICES = [
        ('student', '수강생'),
        ('staff', '운영진'),
    ]
    
    role = forms.ChoiceField(
        label='역할',
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        initial='student'
    )
    
    # 4. 기수 입력 필드
    generation = forms.IntegerField(
        label='기수',
        min_value=1,
        max_value=99,
        initial=24,
        widget=forms.NumberInput(attrs={
            'placeholder': '숫자만 입력하세요 (예: 24)',
            'class': 'generation-input',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )
    
    class Meta:
        model = User
        fields = ('username',)
    
    # --- 검증 로직 (Validation) ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('이미 사용 중인 아이디입니다.')
        return username
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 4:
            raise ValidationError('비밀번호는 최소 4자리 이상이어야 합니다.')
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('두 비밀번호가 일치하지 않습니다.')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        # 주의: role과 generation은 User 모델 필드가 아니므로
        # views.py에서 user.profile.generation 등으로 따로 저장해야 합니다.
        # 여기서는 User 객체만 저장합니다.
        
        if commit:
            user.save()
        return user