from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Student(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ufli_score_1 = models.IntegerField(null=True, blank=True)
    ufli_score_2 = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)  # ✅ Tracks last save

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class StudentGroup(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    due_date = models.DateField()

    def __str__(self):
        return self.title

class Roster(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g. "Period 3 – Reading"
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # stores student list or preview_data

    def __str__(self):
        return f"{self.name} ({self.user.username})"
