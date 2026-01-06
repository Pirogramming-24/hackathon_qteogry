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


# views.py의 signup_view 수정 필요
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 프로필 생성 시 role과 generation 저장
            profile = UserProfile.objects.create(
                user=user,
                role=form.cleaned_data.get('role', 'student'),
                generation=form.cleaned_data.get('generation', 1)
            )
            
            # 자동 로그인
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                return render(request, 'users/signup.html', {
                    'form': form,
                    'show_popup': True,
                    'nickname': profile.nickname,
                    'user': user  # 👈 user 객체 전달
                })
        else:
            return render(request, 'users/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')
