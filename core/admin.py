from django.contrib import admin
from .models import Course, PromptSet, Prompt, Profile, AccessCode

@admin.register(Course, PromptSet, Prompt, Profile, AccessCode)
class ViewAdmin(admin.ModelAdmin):
    pass