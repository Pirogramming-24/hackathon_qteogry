from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse  # 👈 URL 역참조를 위해 추가 필수!
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
                
                # 로그인할 때마다 닉네임 재생성
                new_nickname = profile.regenerate_nickname()
                
                # 👇 역할에 따른 이동 경로 설정 (여기가 핵심입니다)
                if profile.role == 'staff':
                    # 운영진: 세션 생성 페이지로 이동 (원하는 곳으로 변경 가능)
                    next_url = reverse('session_list') 
                else:
                    # 수강생: 세션 목록 페이지로 이동
                    next_url = reverse('session_list')

                # 로그인 성공 시 팝업 표시 및 이동 경로(next_url) 전달
                return render(request, 'users/login.html', {
                    'form': form,
                    'show_popup': True,
                    'nickname': new_nickname,
                    'next_url': next_url  # 👈 템플릿으로 주소 전달
                })
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 1. 프로필 생성 (기존 코드 유지)
            profile = UserProfile.objects.create(
                user=user,
                role=form.cleaned_data.get('role', 'student'),
                generation=form.cleaned_data.get('generation', 1)
            )
            
            # --- 👇 여기가 가장 중요합니다 (누락된 부분) ---
            # 2. 역할이 'staff'면 Django 관리자 권한(is_staff)을 강제로 켜줘야 합니다.
            if profile.role == 'staff':
                user.is_staff = True   # <--- 이 줄이 없으면 403 에러 뜸!
                user.save()            # <--- 변경사항 저장 필수!
                next_url = reverse('session_create')
            else:
                # 수강생은 권한 없음 (명시적으로 꺼주는 것이 안전)
                user.is_staff = False  
                user.save()
                next_url = reverse('session_list')
            # ---------------------------------------------
            
            # 3. 자동 로그인 (기존 코드 유지)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                return render(request, 'users/signup.html', {
                    'form': form,
                    'show_popup': True,
                    'nickname': profile.nickname,
                    'user': user,
                    'next_url': next_url 
                })
        else:
            return render(request, 'users/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')