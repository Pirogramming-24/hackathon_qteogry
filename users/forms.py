from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.ModelForm):
    """
    완전히 커스텀한 회원가입 폼
    Django 기본 검증을 우회하고 우리만의 규칙 적용
    """
    
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={
            'placeholder': '아이디를 입력하세요',
        }),
    )
    
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 입력하세요 (최소 4자리)',
        }),
        help_text='최소 4자리 이상 입력해주세요.'
    )
    
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 다시 입력하세요',
        }),
    )
    
    class Meta:
        model = User
        fields = ('username',)
    
    def clean_username(self):
        """아이디 중복 체크"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('이미 사용 중인 아이디입니다.')
        return username
    
    def clean_password1(self):
        """비밀번호 검증 - 최소 4자리만 체크"""
        password1 = self.cleaned_data.get('password1')
        
        if len(password1) < 4:
            raise ValidationError('비밀번호는 최소 4자리 이상이어야 합니다.')
        
        return password1
    
    def clean_password2(self):
        """비밀번호 확인 검증"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('두 비밀번호가 일치하지 않습니다.')
        
        return password2
    
    def save(self, commit=True):
        """사용자 저장"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
