from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy

from .models import Generation, LiveSession
from .forms import GenerationForm, LiveSessionForm
from django.db.models import Count
from django.core.paginator import Paginator  # 👈 [필수] 이거 꼭 추가해주세요!
from questions.models import Question, UnderstandingCheck


class SessionListView(TemplateView):
    template_name = "live_sessions/session_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        generations = Generation.objects.all()
        generation_id = self.request.GET.get("generation")

        if generation_id:
            try:
                selected_generation = Generation.objects.get(id=generation_id)
            except Generation.DoesNotExist:
                selected_generation = generations.first()
        else:
            selected_generation = generations.first()

        now = timezone.now()

        if selected_generation:
            sessions_qs = (
                LiveSession.objects.filter(generation=selected_generation)
                .order_by("start_at")
            )
            active_sessions = [s for s in sessions_qs if not s.is_archived]
            archived_sessions = [s for s in sessions_qs if s.is_archived]
        else:
            active_sessions = []
            archived_sessions = []

        context.update(
            {
                "generations": generations,
                "selected_generation": selected_generation,
                "active_sessions": active_sessions,
                "archived_sessions": archived_sessions,
                "is_session_owner": self.request.user.is_staff,
            }
        )
        return context


# ---- 운영진(세션자) 전용 Mixin ----
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# ---- 기수 생성 뷰 ----
class GenerationCreateView(StaffRequiredMixin, CreateView):
    model = Generation
    form_class = GenerationForm
    template_name = "live_sessions/generation_form.html"
    success_url = reverse_lazy("live_sessions:session_list")

    def get_success_url(self):
        return f"{reverse('live_sessions:session_list')}?generation={self.object.id}"


# ---- 세션 생성 뷰 ----
class LiveSessionCreateView(StaffRequiredMixin, CreateView):
    model = LiveSession
    form_class = LiveSessionForm
    template_name = "live_sessions/session_form.html"

    def get_initial(self):
        initial = super().get_initial()
        gen_id = self.request.GET.get("generation")
        if gen_id:
            try:
                initial["generation"] = Generation.objects.get(id=gen_id)
            except Generation.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        # 세션자 자동 기록 (users.User 를 쓰고 있다고 가정)
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        gen_id = self.object.generation_id
        return f"{reverse('live_sessions:session_list')}?generation={gen_id}"
    

def session_report(request, pk):
    session = get_object_or_404(LiveSession, pk=pk)
    
    # 1. 질문 유형별 통계
    questions = Question.objects.filter(LiveSession=session)
    concept_count = questions.filter(category='CONCEPT').count()
    error_count = questions.filter(category='ERROR').count()
    etc_count = questions.filter(category='ETC').count()
    
    # 2. 공감 Top 3
    top_questions = questions.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:3]
    
    # 3. 이해도 체크 (전체 가져오기)
    all_checks = UnderstandingCheck.objects.filter(
        session=session, 
        ended_at__isnull=False
    ).order_by('created_at')

    # 👇 [추가] 페이지네이션 로직 (9개씩 자르기)
    paginator = Paginator(all_checks, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'session': session,
        'chart_data': {
            'concept': concept_count,
            'error': error_count,
            'etc': etc_count
        },
        'top_questions': top_questions,
        # 'understanding_checks': understanding_checks,  👈 이거 지우고
        'page_obj': page_obj, # 👈 페이징된 객체를 넘겨줍니다.
    }
    
    return render(request, 'live_sessions/session_report.html', context)

# live_sessions/views.py 맨 아래에 추가

def session_archive(request, pk):
    """
    세션 아카이브 상태를 변경하는 함수
    """
    if request.method == "POST":
        session = get_object_or_404(LiveSession, pk=pk)
        # 상태 변경 (True <-> False)
        session.is_archived_manual = not session.is_archived_manual
        session.save()
        
    return redirect('live_sessions:session_list')