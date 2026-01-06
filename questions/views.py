from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, UnderstandingCheck, UnderstandingResponse
from .forms import UnderstandingForm
from live_sessions.models import LiveSession, LiveSessionMember
from django.db import transaction

# Create your views here.

def questions_read(request, pk):
    question = Question.objects.get(id=pk)
    
    context = {
        "question" : question
    }
    return render(request, "questions_read.html", context)


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

            return redirect(
                "questions:understanding_check",
                pk=understanding_check.pk
            )

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