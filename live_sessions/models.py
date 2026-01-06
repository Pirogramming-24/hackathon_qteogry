from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Generation(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class LiveSession(models.Model):
    generation = models.ForeignKey(
        Generation,
        related_name="sessions",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)

    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)



    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_sessions",
    )

    is_archived_manual = models.BooleanField(
        default=False,
        help_text="운영진이 수동으로 아카이브 처리할 때 사용",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_at"]

    def __str__(self):
        return f"[{self.generation}] {self.title}"

    @property
    def is_archived(self) -> bool:
        """
        종료 시간이 있으면 종료 기준으로, 없으면 시작 기준으로
        지난 세션인지 판단.
        """
        ref = self.end_at or self.start_at
        return self.is_archived_manual or ref < timezone.now()
