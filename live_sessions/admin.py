from django.contrib import admin
from .models import Generation, LiveSession


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "order")
    ordering = ("order",)


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "generation", "start_at", "end_at", "is_archived_manual")
    list_filter = ("generation", "is_archived_manual")
    search_fields = ("title",)
