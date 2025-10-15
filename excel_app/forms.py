from django import forms
from django.forms import formset_factory

class StudentForm(forms.Form):
    name = forms.CharField(max_length=100, label="Student Name")
    score_c1 = forms.IntegerField(label="Score C1", required=False)
    score_c2 = forms.IntegerField(label="Score C2", required=False)

StudentFormSet = formset_factory(StudentForm, extra=25, max_num=25)
