import json
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Question, UnderstandingCheck, UnderstandingResponse, Comment, Like
from .forms import UnderstandingForm, QuestionForm, CommentForm
from realtime.services import publish_session_event
from live_sessions.models import LiveSession, LiveSessionMember
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone # 👈 상단에 import 추가


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

    elif sort_mode == 'pending':
        questions = questions.filter(status='OPEN').order_by('-created_at')
    
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
    
    comments = Comment.objects.filter(question=selected_question).select_related("user").order_by("created_at")
    Cform = CommentForm()

    if request.method == "POST":
        Cform = CommentForm(request.POST)
        if Cform.is_valid():
            new_comment = Cform.save(commit=False)
            new_comment.user = request.user
            new_comment.question = selected_question
            new_comment.save()
            # 실시간 추가 
            publish_session_event(str(session.id), "comment:new", {
                "comment_id": new_comment.id,
                "question_id": selected_question.id,
            })

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
        'qform': QuestionForm(),
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



@login_required
def understanding_check_upload(request):
    # 임시 세션 (나중엔 URL에서 받아오도록 수정 필요할 수 있음)
    session = LiveSession.objects.first()

    if request.method == "POST":
        form = UnderstandingForm(request.POST)
        if form.is_valid():
            # 1. [핵심] 기존에 활성화된(is_current=True) 체크가 있다면 모두 False로 변경 (아카이브로 보냄)
            UnderstandingCheck.objects.filter(session=session, is_current=True).update(is_current=False)
            
            # 2. 새 체크 생성
            understanding_check = form.save(commit=False)
            understanding_check.session = session
            understanding_check.is_current = True
            understanding_check.save()
            # 실시간 추가

            return redirect("questions:question_main", session.pk)
    else:
        form = UnderstandingForm()

    return render(request, "understanding_check_upload.html", {"form": form})

# 👇 [추가] 진행 중인 체크를 강제로 종료(취소)하는 기능
@login_required
def understanding_check_finish(request, check_id):
    check = get_object_or_404(UnderstandingCheck, id=check_id)
    
    # 이미 끝난 게 아니라면 현재 시간으로 종료 처리
    if not check.ended_at:
        check.ended_at = timezone.now()
        check.save()
    
    # 해당 세션 메인 페이지로 돌아가기
    return redirect("questions:question_main", check.session.id)

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

    
    
@login_required
def understanding_check_respond(request):
    check_id = request.POST.get("check_id")
    check = get_object_or_404(UnderstandingCheck, id=check_id)

    # 1. 응답 저장 (기존 로직)
    response, created = UnderstandingResponse.objects.get_or_create(
        understanding_check=check,
        user=request.user
    )

    # 2. 현재 응답 수 카운트
    response_count = check.responses.count()
    
    # 3. [핵심] 목표 인원 달성 시 종료 시간(ended_at) 기록
    # 이미 끝난 거면(ended_at이 있으면) 기록 안 함
    if check.ended_at is None and response_count >= check.target_response_count:
        check.ended_at = timezone.now()
        check.save()
        is_finished = True
    else:
        is_finished = bool(check.ended_at) # 이미 끝났는지 여부

    # (기존 진행률 로직)
    total_count = check.target_response_count # 👈 전체 인원 대신 목표 인원 기준으로 변경 추천
    progress = int((response_count / total_count) * 100) if total_count else 0

    return JsonResponse({
        "created": created,
        "response_count": response_count,
        "total_count": total_count,
        "progress": progress,
        "is_finished": is_finished, # 👈 프론트엔드에 "끝났다"고 알려줌
        "duration": check.duration_seconds # 👈 현재까지 걸린 시간도 전송
    })
    
@login_required
def question_main(request, session_id):
    session = get_object_or_404(LiveSession, pk=session_id)
    
    # 1. 질문 리스트 및 정렬 (헬퍼 함수 사용)
    questions, sort_mode = get_sorted_questions(request, session)

    # 2. 질문 작성 로직 (POST 요청 처리)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.user = request.user
            new_question.LiveSession = session
            new_question.save()
            # 실시간
            publish_session_event(str(session_id), "question:new", {
                "question_id": new_question.id,
            })
            return redirect('questions:question_main', session_id=session.id)
    else:
        form = QuestionForm()

    # 3. [수정] 이해도 체크 가져오기 (중복 제거 및 목표 인원 연동)
    understanding_check = (
        UnderstandingCheck.objects
        .filter(session=session, is_current=True)
        .order_by("-created_at")
        .first()
    )

    if understanding_check:
        response_count = understanding_check.responses.count()
        # 👇 [핵심] 하드코딩(24) 대신, DB에 저장된 목표 인원을 사용!
        total_count = understanding_check.target_response_count 
        progress = int((response_count / total_count) * 100) if total_count else 0
    else:
        response_count = 0
        total_count = 0
        progress = 0

    context = {
        'session': session,
        'questions': questions,
        'qform': form,
        'sort_mode': sort_mode, # 현재 어떤 탭이 활성화되었는지 표시하기 위함
        
        'understanding_check': understanding_check,
        'response_count': response_count,
        'total_count': total_count, # 👈 이제 템플릿에서 목표 인원을 제대로 표시함
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
        # 실시간 추가 상태변경
        publish_session_event(str(question.LiveSession), "question:new", {
            "question_id": question.id,
        })

        return JsonResponse({'status': new_status, 'message': 'Status updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    
@login_required
def comment_delete(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id)

        # ⭐ 본인 댓글인지 체크
        if comment.user != request.user:
            return JsonResponse({"success": False, "error": "권한 없음"}, status=403)

        comment.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)
def comment_partial(request, session_id, question_id, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("user", "question"),
        id=comment_id,
        question_id=question_id,
        question__LiveSession_id=session_id,
    )

    html = render_to_string(
        "partials/comment_item.html",
        {"c": comment},
        request=request,
    )
    return HttpResponse(html)

def question_partial(request, session_id, question_id):
    q = get_object_or_404(
        Question.objects.select_related("user", "LiveSession"),
        id=question_id,
        LiveSession_id=session_id,
    )


    sort_mode = request.GET.get("sort", "all")  # 링크 유지용

    html = render_to_string(
        "partials/question_item.html",
        {
            "q": q,
            "session": q.LiveSession,  # ✅ 템플릿에서 session.id 쓰게 보장
            "sort_mode": sort_mode
        },
        request=request,
    )
    return HttpResponse(html)




