# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student  # adjust if Student is in a different app

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class AddStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "ufli_score_1", "ufli_score_2"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Student name"}),
            "ufli_score_1": forms.NumberInput(attrs={"placeholder": "Score 1"}),
            "ufli_score_2": forms.NumberInput(attrs={"placeholder": "Score 2"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ufli_score_1"].required = False
        self.fields["ufli_score_2"].required = False
