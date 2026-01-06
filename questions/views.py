from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Question, UnderstandingCheck, UnderstandingResponse, Comment
from .forms import UnderstandingForm, QuestionForm
from live_sessions.models import LiveSession, LiveSessionMember
from django.db import transaction

# def questions_read(request, pk):
#     question = Question.objects.get(id=pk)
    
#     context = {
#         "question" : question
#     }
#     return render(request, "questions_read.html", context)

def question_detail(request, session_id, question_id):
    # 1. 기본 데이터 (리스트 출력을 위해 필요)
    session = get_object_or_404(LiveSession, pk=session_id)
    questions = Question.objects.filter(LiveSession=session).order_by('-created_at')
    
    # 2. 선택된 질문 데이터 가져오기
    selected_question = get_object_or_404(Question, pk=question_id)
    
    # 3. 댓글 데이터 가져오기 (선택된 질문에 달린 댓글들)
    comments = Comment.objects.filter(question=selected_question).order_by('created_at')

    context = {
        'session': session,
        'questions': questions,
        'selected_question': selected_question, # 이게 있으면 상세뷰가 뜸
        'comments': comments,
        'like_count': selected_question.likes.count(),
        'sort_mode': 'all', # 상세뷰에서는 정렬 기본값
    }
    
    return render(request, 'questions/main_ny.html', context)

def understanding_check(request, pk):
    understanding_check = get_object_or_404(
        UnderstandingCheck,
        pk=pk
    )

    responses = understanding_check.responses.all()
    response_count = responses.count()
    
    total_members = 24 #임의값

    context = {
        "understanding_check": understanding_check,
        "response_count": response_count,
        "responses": responses,
        "total_count": total_members,
    }

    return render(
        request,
        "understanding_check.html",
        context
    )

    
    
    
    # understanding_check = UnderstandingCheck.objects.get(id=pk)
    # understandingResponse = UnderstandingResponse.objects.get(id=pk)
    
    # context = {
    #     "understanding_check" : understanding_check,
    #     "understandingResponse" : understandingResponse,
        
    # }
    # return render(request, understanding_check.html, context)



# @login_required




def understanding_check_upload(request):
    # 임시 세션 하나 가져오기 (없으면 에러 나도 OK)
    session = LiveSession.objects.first()

    if request.method == "POST":
        form = UnderstandingForm(request.POST)
        if form.is_valid():
            understanding_check = form.save(commit=False)
            understanding_check.session = session
            understanding_check.is_current = True
            understanding_check.save()

            return redirect("questions:question_main", session.pk)


    else:
        form = UnderstandingForm()

    return render(request, "understanding_check_upload.html", {"form": form})

# def understanding_check_upload(request):
#     if request.method == "POST": 
#         form = UnderstandingForm(request.POST)
#         if form.is_valid(): 
#             understanding_check = form.save()
#             return redirect(
#                 "questions:understanding_check",
#                 pk=understanding_check.pk
#             )
#     else:
#         form = UnderstandingForm()

#     return render(
#         request,
#         "understanding_check_upload.html",
#         { "form": form }
#     )

    
    
def understanding_check_respond(request):
    check_id = request.POST.get("check_id")
    check = get_object_or_404(UnderstandingCheck, id=check_id)

    # 이미 응답했는지 확인
    response, created = UnderstandingResponse.objects.get_or_create(
        understanding_check=check,
        user=request.user
    )

    response_count = check.responses.count()
    total_count = LiveSessionMember.objects.filter(
        session=check.session,
        role=LiveSessionMember.Role.LISTENER
    ).count()

    progress = int((response_count / total_count) * 100) if total_count else 0

    return JsonResponse({
        "created": created,  # 새 응답인지 여부
        "response_count": response_count,
        "total_count": total_count,
        "progress": progress,
    })
    
    
@login_required
def question_main(request, session_id):
    # 1. 현재 접속한 라이브 세션 가져오기
    session = get_object_or_404(LiveSession, pk=session_id)
    
    # 2. 필터링 및 정렬 로직 (GET 파라미터 처리)
    sort_mode = request.GET.get('sort', 'all') # 기본값은 전체 보기
    
    # 해당 세션의 질문들만 가져오기
    questions = Question.objects.filter(LiveSession=session)
    
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

    
    # 5. 이해도 체크 (main_ny 전용)
    understanding_check = UnderstandingCheck.objects.filter(
        session=session,
        is_current=True
    ).first()

    if understanding_check:
        response_count = understanding_check.responses.count()
        total_count = session.livesessionmember_set.count()
        progress = int(response_count / total_count * 100) if total_count else 0
    else:
        response_count = 0
        total_count = 0
        progress = 0

    # 3. 질문 작성 로직 (POST 요청 처리)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.user = request.user      # 현재 로그인한 유저 연결
            new_question.LiveSession = session   # 현재 세션 연결
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
        'understanding_check': understanding_check,
        'response_count': response_count,
        'total_count': total_count,
        'progress': progress,
    }
    
    return render(request, 'questions/main_ny.html', context)