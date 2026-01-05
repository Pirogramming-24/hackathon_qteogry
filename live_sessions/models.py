from django.db import models
from django.conf import settings

# Create your models here.


class LiveSession(models.Model):
    code = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=255, default="my session")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LiveSessionMember(models.Model):
    class Role(models.TextChoices):
        HOST = "HOST", "운영진"
        LISTENER = "LISTENER", "청취자"

    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=Role.choices)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "user")
