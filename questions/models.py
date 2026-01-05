
from django.conf import settings
from django.db import models
from live_sessions.models import LiveSession

# Create your models here.
# TODO:- timing 변수 빼야함
class Question(models.Model):
    class Category(models.TextChoices):
        CONCEPT = "CONCEPT", "개념"
        ERROR = "ERROR", "오류"
        ETC = "ETC", "기타"

    class Timing(models.TextChoices):
        NOW = "NOW", "지금 급해요"
        BREAK = "BREAK", "쉬는 시간에"
        LATER = "LATER", "끝나고"

    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="questions/",
        blank=True,
        null=True
    )
    content = models.TextField()

    category = models.CharField(max_length=20, choices=Category.choices)
    timing = models.CharField(max_length=20, choices=Timing.choices)

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
