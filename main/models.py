from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ufli_score_1 = models.IntegerField(null=True, blank=True)
    ufli_score_2 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"