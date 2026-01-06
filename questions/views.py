from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Question, LiveSession
from .forms import QuestionForm

# Create your views here.
@login_required
def question_main(request, session_id):
    # 1. 현재 접속한 라이브 세션 가져오기
    session = get_object_or_404(LiveSession, pk=session_id)
    
    # 2. 필터링 및 정렬 로직 (GET 파라미터 처리)
    sort_mode = request.GET.get('sort', 'all') # 기본값은 전체 보기
    
    # 해당 세션의 질문들만 가져오기
    questions = Question.objects.filter(live_session=session)
    
    if sort_mode == 'concept':
        # 개념 질문만 필터링
        questions = questions.filter(category='CONCEPT')
        
    elif sort_mode == 'likes':
        # 공감 순 정렬
        questions = questions.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        
    elif sort_mode == 'my':
        # 내 질문만 보기
        questions = questions.filter(user=request.user)
    
    else:
        # 기본: 최신순 정렬
        questions = questions.order_by('-created_at')

    # 3. 질문 작성 로직 (POST 요청 처리)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.user = request.user      # 현재 로그인한 유저 연결
            new_question.live_session = session   # 현재 세션 연결
            new_question.save()
            # 작성이 끝나면 현재 페이지로 리다이렉트 (새로고침 시 중복 전송 방지)
            return redirect('questions:question_main', session_id=session.id)
    else:
        form = QuestionForm()

    # 4. 템플릿에 전달할 데이터
    context = {
        'session': session,
        'questions': questions,
        'form': form,
        'sort_mode': sort_mode, # 현재 어떤 탭이 활성화되었는지 표시하기 위함
    }
    
    return render(request, 'questions/main_ny.html', context)