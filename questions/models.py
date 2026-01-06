
from django.conf import settings
from django.db import models
from live_sessions.models import LiveSession

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

class UnderstandingCheck(models.Model):
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name="understanding_checks"
    )

    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    is_current = models.BooleanField(default=False)


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
