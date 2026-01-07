import json
import random  # 👈 닉네임 랜덤 생성용
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Question, UnderstandingCheck, UnderstandingResponse, Comment, Like
from .forms import UnderstandingForm, QuestionForm, CommentForm
from live_sessions.models import LiveSession, LiveSessionMember
from realtime.services import publish_session_event  # 실시간 기능이 있다면 유지


# ✅ [헬퍼 함수] 질문 정렬 및 최적화 (N+1 문제 해결)
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
    sort_mode = request.GET.get('sort', 'all')
    
    # select_related와 annotate로 DB 쿼리 최소화
    questions = (
        Question.objects
        .filter(LiveSession=session)
        .select_related("user")
        .annotate(like_count=Count("likes"))
    )
    
    if sort_mode == 'concept':
        questions = questions.filter(category='CONCEPT').order_by('-created_at')
    elif sort_mode == 'likes':
        questions = questions.order_by('-like_count', '-created_at')
    elif sort_mode == 'my':
        if request.user.is_authenticated:
            questions = questions.filter(user=request.user).order_by('-created_at')
        else:
            questions = Question.objects.none()
    elif sort_mode == 'pending':
        questions = questions.filter(status='OPEN').order_by('-created_at')
    else:
        questions = questions.order_by('-created_at')
        sort_mode = 'all'
        
    return questions, sort_mode


# ✅ [메인 뷰] 질문 리스트, 닉네임 처리, 채팅방 입장 통합
@login_required
def question_main(request, session_id):
    session = get_object_or_404(LiveSession, pk=session_id)
    
    # 1. [닉네임] 입장 시 랜덤 닉네임 자동 할당 (다운로드 로직)
    member, created = LiveSessionMember.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={'role': 'LISTENER'}
    )
    
    # 처음 왔거나 닉네임이 없으면 랜덤 생성
    if created or not member.nickname:
        adjectives = ["지친", "행복한", "졸린", "배고픈", "신난", "우울한", "즐거운", "똑똑한"]
        nouns = ["코끼리", "사자", "토끼", "판다", "강아지", "고양이", "호랑이", "펭귄"]
        random_nickname = f"{random.choice(adjectives)} {random.choice(nouns)}"
        member.nickname = random_nickname
        member.save()

    # 2. 질문 리스트 가져오기 (최적화 적용됨)
    questions, sort_mode = get_sorted_questions(request, session)

    # 3. [닉네임] 작성자 매핑 (화면에 보여줄 때 닉네임으로 바꿔치기)
    members = LiveSessionMember.objects.filter(session=session).values('user_id', 'nickname')
    nickname_map = { m['user_id']: m['nickname'] for m in members }
    
    for q in questions:
        # 닉네임 지도에 있으면 닉네임 사용, 없으면 아이디 사용
        q.display_name = nickname_map.get(q.user_id, q.user.username)

    # 4. 이해도 체크 로직
    understanding_check = (
        UnderstandingCheck.objects
        .filter(session=session, is_current=True)
        .order_by("-created_at")
        .first()
    )

    if understanding_check:
        response_count = understanding_check.responses.count()
        total_count = understanding_check.target_response_count 
        progress = int((response_count / total_count) * 100) if total_count else 0
    else:
        response_count = 0
        total_count = 0
        progress = 0

    # 5. 질문 작성 폼 처리 (POST)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.user = request.user
            new_question.LiveSession = session
            new_question.save()
            
            # 실시간 이벤트 (선택사항)
            try:
                publish_session_event(str(session_id), "question:new", {
                    "question_id": new_question.id,
                })
            except:
                pass # 에러 무시
                
            return redirect('questions:question_main', session_id=session.id)
    else:
        form = QuestionForm()

    context = {
        'session': session,
        'questions': questions,
        'qform': form,  # HTML에서 {{ qform }} 사용
        'sort_mode': sort_mode,
        'understanding_check': understanding_check,
        'response_count': response_count,
        'total_count': total_count,
        'progress': progress,
    }
    
    return render(request, 'questions/main_ny.html', context)


# ✅ 질문 상세 보기
def question_detail(request, session_id, question_id):
    session = get_object_or_404(LiveSession, pk=session_id)
    questions, sort_mode = get_sorted_questions(request, session)
    selected_question = get_object_or_404(Question, pk=question_id)
    
    # 상세 페이지에서도 닉네임 매핑 필요
    members = LiveSessionMember.objects.filter(session=session).values('user_id', 'nickname')
    nickname_map = { m['user_id']: m['nickname'] for m in members }
    
    # 리스트의 닉네임 매핑
    for q in questions:
        q.display_name = nickname_map.get(q.user_id, q.user.username)
        
    # 선택된 질문의 작성자 닉네임 매핑
    selected_question.display_name = nickname_map.get(selected_question.user_id, selected_question.user.username)
    
    comments = Comment.objects.filter(question=selected_question).select_related("user").order_by("created_at")
    
    # 댓글 작성자 닉네임 매핑
    for c in comments:
        c.display_name = nickname_map.get(c.user_id, c.user.username)

    Cform = CommentForm()

    if request.method == "POST":
        Cform = CommentForm(request.POST)
        if Cform.is_valid():
            new_comment = Cform.save(commit=False)
            new_comment.user = request.user
            new_comment.question = selected_question
            new_comment.save()
            
            try:
                publish_session_event(str(session.id), "comment:new", {
                    "comment_id": new_comment.id,
                    "question_id": selected_question.id,
                })
            except:
                pass
            return redirect("questions:question_detail", session_id=session.id, question_id=selected_question.id)

    context = {
        'session': session,
        'questions': questions,
        'selected_question': selected_question,
        'question': selected_question, # 템플릿 호환성용
        'comments': comments,
        'cform': Cform,
        'like_count': selected_question.likes.count(),
        'sort_mode': sort_mode,
        'qform': QuestionForm(),
    }
    
    return render(request, 'questions/main_ny.html', context)


# ✅ 이해도 체크 생성 (운영진용)
@login_required
def understanding_check_upload(request, session_id):
    session = get_object_or_404(LiveSession, pk=session_id) # 추후 session_id 인자로 받도록 개선 가능

    if request.method == "POST":
        form = UnderstandingForm(request.POST)
        if form.is_valid():
            UnderstandingCheck.objects.filter(session=session, is_current=True).update(is_current=False)
            understanding_check = form.save(commit=False)
            understanding_check.session = session
            understanding_check.is_current = True
            understanding_check.save()
            return redirect("questions:question_main", session.pk)
    else:
        form = UnderstandingForm()

    return render(request, "questions/understanding_check_upload.html", {"form": form})


# ✅ 이해도 체크 종료
@login_required
def understanding_check_finish(request, check_id):
    check = get_object_or_404(UnderstandingCheck, id=check_id)
    if not check.ended_at:
        check.ended_at = timezone.now()
        check.save()
    return redirect("questions:question_main", check.session.id)


# ✅ 이해도 체크 응답 (청취자용)
@login_required
def understanding_check_respond(request):
    check_id = request.POST.get("check_id")
    check = get_object_or_404(UnderstandingCheck, id=check_id)

    response, created = UnderstandingResponse.objects.get_or_create(
        understanding_check=check,
        user=request.user
    )
    
    response_count = check.responses.count()
    
    if check.ended_at is None and response_count >= check.target_response_count:
        check.ended_at = timezone.now()
        check.save()
        is_finished = True
    else:
        is_finished = bool(check.ended_at)

    total_count = check.target_response_count
    progress = int((response_count / total_count) * 100) if total_count else 0

    return JsonResponse({
        "created": created,
        "response_count": response_count,
        "total_count": total_count,
        "progress": progress,
        "is_finished": is_finished,
        "duration": check.duration_seconds
    })


# ✅ 질문 좋아요 토글
@require_POST
def question_like(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    question = get_object_or_404(Question, pk=question_id)
    user = request.user

    if question.likes.filter(user=user).exists():
        question.likes.filter(user=user).delete()
        liked = False
    else:
        Like.objects.create(question=question, user=user)
        liked = True

    return JsonResponse({'liked': liked, 'count': question.likes.count()})


# ✅ 질문 상태 변경 (운영진용)
@require_POST
def question_update_status(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        question = get_object_or_404(Question, pk=question_id)
        question.status = new_status
        question.save()
        
        try:
            publish_session_event(str(question.LiveSession.id), "question:update", {"question_id": question.id})
        except:
            pass
            
        return JsonResponse({'status': new_status, 'message': 'Status updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ✅ 댓글 삭제
@login_required
def comment_delete(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user != request.user:
            return JsonResponse({"success": False, "error": "권한 없음"}, status=403)
        comment.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


# ✅ 부분 렌더링 (HTMX/실시간용)
def question_partial(request, session_id, question_id):
    q = get_object_or_404(
        Question.objects.select_related("user", "LiveSession"),
        id=question_id,
        LiveSession_id=session_id,
    )
    # 부분 렌더링 시에도 닉네임 매핑 필요
    try:
        member = LiveSessionMember.objects.get(session=q.LiveSession, user=q.user)
        q.display_name = member.nickname
    except LiveSessionMember.DoesNotExist:
        q.display_name = q.user.username

    sort_mode = request.GET.get("sort", "all")
    html = render_to_string(
        "partials/question_item.html",
        {"q": q, "session": q.LiveSession, "sort_mode": sort_mode},
        request=request,
    )
    return HttpResponse(html)


def comment_partial(request, session_id, question_id, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("user", "question"),
        id=comment_id,
        question_id=question_id,
        question__LiveSession_id=session_id,
    )
    # 부분 렌더링 시에도 닉네임 매핑 필요
    try:
        member = LiveSessionMember.objects.get(session__id=session_id, user=comment.user)
        comment.display_name = member.nickname
    except LiveSessionMember.DoesNotExist:
        comment.display_name = comment.user.username

    html = render_to_string(
        "partials/comment_item.html",
        {"c": comment},
        request=request,
    )
    return HttpResponse(html)

# questions/views.py 맨 아래에 추가

# ✅ 개별 이해도 체크 페이지 (urls.py 에러 방지용)
def understanding_check(request, pk):
    understanding_check = get_object_or_404(UnderstandingCheck, pk=pk)
    responses = understanding_check.responses.all()
    response_count = responses.count()
    
    # 목표 인원이 설정되어 있다면 그것을 사용, 없으면 기본값 24
    total_count = understanding_check.target_response_count if understanding_check.target_response_count else 24

    context = {
        "understanding_check": understanding_check,
        "response_count": response_count,
        "responses": responses,
        "total_count": total_count,
    }
    
    # 템플릿 파일이 있는지 확인 필요 (없으면 에러 날 수 있음)
    return render(request, "understanding_check.html", context)