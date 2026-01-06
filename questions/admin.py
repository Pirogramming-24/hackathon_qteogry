from django.contrib import admin

# Register your models here.
from .models import Question, Comment


# Register your models here.
admin.site.register(Question)
admin.site.register(Comment)
