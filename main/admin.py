from django.contrib import admin
from .models import Student, StudentGroup, Assignment, Profile

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher", "ufli_score_1", "ufli_score_2", "last_updated")

@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher")

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "due_date")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "has_paid")
