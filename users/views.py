from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms import CustomUserCreationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # 프로필 확인 및 생성
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # 👇 로그인할 때마다 닉네임 재생성
                new_nickname = profile.regenerate_nickname()
                
                # 로그인 성공 시 팝업 표시
                return render(request, 'users/login.html', {
                    'form': form,
                    'show_popup': True,
                    'nickname': new_nickname
                })
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        # 👇 커스텀 폼 사용
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 사용자 생성
            user = form.save()
            
            # 프로필 자동 생성 (save 메서드에서 랜덤 닉네임 생성됨)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # 자동 로그인 처리
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # 회원가입 성공 시 닉네임 팝업 표시
                return render(request, 'users/signup.html', {
                    'form': form,
                    'show_popup': True,
                    'nickname': profile.nickname
                })
        else:
            # 폼 에러가 있을 경우 에러 메시지와 함께 다시 렌더링
            return render(request, 'users/signup.html', {'form': form})
    else:
        # 👇 커스텀 폼 사용
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('users:login')
