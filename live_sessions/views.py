from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy

from .models import Generation, LiveSession
from .forms import GenerationForm, LiveSessionForm


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
