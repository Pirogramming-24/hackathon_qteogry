import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Question, UnderstandingCheck, UnderstandingResponse, Comment, Like
from .forms import UnderstandingForm, QuestionForm, CommentForm
from live_sessions.models import LiveSession, LiveSessionMember
from django.db import transaction
from django.views.decorators.http import require_POST

# def questions_read(request, pk):
#     question = Question.objects.get(id=pk)
    
#     context = {
#         "question" : question
#     }
#     return render(request, "questions_read.html", context)

def get_sorted_questions(request, session):
    sort_mode = request.GET.get('sort', 'all') # URL에서 sort 파라미터 가져오기
    questions = Question.objects.filter(LiveSession=session)
    
    if sort_mode == 'concept':
        # 개념 질문만 필터링 + 최신순 정렬
        questions = questions.filter(category='CONCEPT').order_by('-created_at')
        
    elif sort_mode == 'likes':
        # 공감 순 정렬 (공감수 내림차순 -> 최신순)
        questions = questions.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        
    elif sort_mode == 'my':
        # 내 질문만 보기 + 최신순 정렬
        if request.user.is_authenticated:
            questions = questions.filter(user=request.user).order_by('-created_at')
        else:
            questions = Question.objects.none() # 로그인 안했으면 빈 리스트
    
    else:
        # 기본: 최신순 정렬
        questions = questions.order_by('-created_at')
        sort_mode = 'all' # 이상한 값이 들어오면 all로 처리
        
    return questions, sort_mode

def question_detail(request, session_id, question_id):
    # 1. 기본 데이터 (리스트 출력을 위해 필요)
    session = get_object_or_404(LiveSession, pk=session_id)
    # questions = Question.objects.filter(LiveSession=session).order_by('-created_at')
    questions, sort_mode = get_sorted_questions(request, session)
    
    # 2. 선택된 질문 데이터 가져오기
    selected_question = get_object_or_404(Question, pk=question_id)
    
    comments = Comment.objects.filter(question=selected_question).select_related("user").order_by("-created_at")
    Cform = CommentForm()

    if request.method == "POST":
        Cform = CommentForm(request.POST)
        if Cform.is_valid():
            new_comment = Cform.save(commit=False)
            new_comment.user = request.user
            new_comment.question = selected_question
            new_comment.save()
            return redirect("questions:question_detail", session_id=session.id, question_id=selected_question.id)

    context = {
        'session': session,
        'questions': questions,
        "question": selected_question,\
        'selected_question': selected_question, # 이게 있으면 상세뷰가 뜸
        'comments': comments,
        "cform": Cform,
        'like_count': selected_question.likes.count(),
        'sort_mode': sort_mode, # 상세뷰에서는 정렬 기본값
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
    session = get_object_or_404(LiveSession, pk=session_id)
    
    # [수정] 헬퍼 함수를 사용해 질문 리스트와 현재 정렬 모드 가져오기
    questions, sort_mode = get_sorted_questions(request, session)

    
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
            new_question.user = request.user
            new_question.LiveSession = session
            new_question.save()
            return redirect('questions:question_main', session_id=session.id)
    else:
        form = QuestionForm()
        
        
    # 최신 understanding check 가져오기
    understanding_check = (
        UnderstandingCheck.objects
        .filter(session=session, is_current=True)
        .order_by("-created_at")
        .first()
    )
    if understanding_check:
        response_count = understanding_check.responses.count()
        total_count = session.livesessionmember_set.count()
        progress = int((response_count / total_count) * 100) if total_count else 0
    else:
        response_count = 0
        total_count = 0
        progress = 0


    context = {
        'session': session,
        'questions': questions,
        'form': form,
        'sort_mode': sort_mode, # 현재 어떤 탭이 활성화되었는지 표시하기 위함
        'understanding_check': understanding_check,
        'response_count': response_count,
        'total_count': total_count,
        'progress': progress,
        
        'understanding_check': understanding_check,
        'response_count': response_count,
        'total_count': total_count,
        'progress': progress,
    }
    
    return render(request, 'questions/main_ny.html', context)

@require_POST
def question_like(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    question = get_object_or_404(Question, pk=question_id)
    user = request.user

    # 이미 좋아요를 눌렀는지 확인
    if question.likes.filter(user=user).exists():
        # 이미 눌렀으면 삭제 (좋아요 취소)
        question.likes.filter(user=user).delete()
        liked = False
    else:
        # 안 눌렀으면 추가 (좋아요)
        Like.objects.create(question=question, user=user)
        liked = True

    context = {
        'liked': liked,
        'count': question.likes.count()
    }
    return JsonResponse(context)

@require_POST
def question_update_status(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    try:
        data = json.loads(request.body)
        new_status = data.get('status') # 'OPEN' 또는 'ANSWERED'

        question = get_object_or_404(Question, pk=question_id)
        question.status = new_status
        question.save()

        return JsonResponse({'status': new_status, 'message': 'Status updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)