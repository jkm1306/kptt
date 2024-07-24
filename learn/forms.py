from django import forms
from django.forms import modelformset_factory
from .models import Student, StudentChapterCompletion


class StudentGradeForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ("user", "student_slug")


StudentGradeFormSet = modelformset_factory(Student, form=StudentGradeForm, extra=1)


class StudentProgressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_student = kwargs.pop('current_student', None)
        super(StudentProgressForm, self).__init__(*args, **kwargs)
        if current_student:
            self.fields['student'].initial = current_student

    class Meta:
        model = StudentChapterCompletion
        fields = ["completed", "student", "chapter"]
        widgets = {
            "student": forms.HiddenInput(),
            "chapter": forms.HiddenInput(),
        }