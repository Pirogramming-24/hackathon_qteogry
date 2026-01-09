
from django.conf import settings
from django.db import models
from live_sessions.models import LiveSession

from django.utils import timezone
import statistics  # 중앙값 계산을 위해 필요

# Create your models here.

class Question(models.Model):
    class Category(models.TextChoices):
        CONCEPT = "CONCEPT", "개념"
        ERROR = "ERROR", "오류"
        ETC = "ETC", "기타"

    LiveSession = models.ForeignKey(LiveSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="questions/",
        blank=True,
        null=True
    )
    content = models.TextField()

    category = models.CharField(max_length=20, choices=Category.choices)

    status = models.CharField(
        max_length=20,
        choices=[("OPEN", "대기"), ("ANSWERED", "답변완료")],
        default="OPEN",
    )

    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "user")

# 수정버전
class UnderstandingCheck(models.Model):
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name="understanding_checks"
    )
    content = models.CharField(max_length=255)
    
    # 👇 [수정] 목표 인원 설정 (기본값 24명 예시)
    target_response_count = models.IntegerField(default=20, help_text="목표 응답 인원")
    
    # 👇 [수정] 타이머 기록용 필드
    created_at = models.DateTimeField(auto_now_add=True) # 시작 시간 (생성 즉시 시작)
    ended_at = models.DateTimeField(null=True, blank=True) # 종료 시간 (목표 달성 시 기록)
    
    is_current = models.BooleanField(default=False)

    @property
    def duration_seconds(self):
        """걸린 시간(초) 계산"""
        if self.ended_at:
            delta = self.ended_at - self.created_at
            return delta.total_seconds()
        
        # 아직 안 끝났으면 현재까지 걸린 시간
        delta = timezone.now() - self.created_at
        return delta.total_seconds()

    @property
    def difficulty_level(self):
        """
        데이터 기반 난이도 분석 (상대적 평가)
        다른 모든 종료된 체크들의 중앙값과 비교하여 난이도를 반환
        """
        # 1. 이 세션(또는 전체 세션)의 '완료된' 이해도 체크들을 가져옴
        completed_checks = UnderstandingCheck.objects.filter(
            session=self.session, 
            ended_at__isnull=False
        ).exclude(id=self.id) # 자기 자신 제외

        if not completed_checks.exists():
            return "데이터 수집 중..." # 비교군이 없음

        # 2. 다른 체크들의 소요 시간 리스트 생성
        durations = [c.duration_seconds for c in completed_checks]
        
        # 3. 중앙값(Median) 계산
        median_time = statistics.median(durations)
        
        # 4. 내 기록과 중앙값 비교 (내 기록이 0이면 계산 불가)
        if self.duration_seconds == 0: return "측정 중"
        
        # 비율 계산: (내 시간 / 중앙값) * 100
        # 예: 중앙값이 30초인데 내가 60초 걸렸으면 200% (어려움)
        ratio = (self.duration_seconds / median_time) * 100
        
        if ratio > 150:
            return "🔥 매우 어려움" # 남들보다 1.5배 더 오래 걸림
        elif ratio > 120:
            return "💦 조금 어려움"
        elif ratio < 80:
            return "😎 쉬움"
        else:
            return "😐 보통"


class UnderstandingResponse(models.Model):
    understanding_check = models.ForeignKey(
        UnderstandingCheck,
        on_delete=models.CASCADE,
        related_name="responses"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("understanding_check", "user")
