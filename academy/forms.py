from django import forms

from accounts.models import User

from .models import ClassRoutine, Exam, ExamResult, FeePayment, Notice, SchoolClass, Subject


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "section", "order"]


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "school_class", "code"]


class ClassRoutineForm(forms.ModelForm):
    class Meta:
        model = ClassRoutine
        fields = ["school_class", "subject", "teacher", "day", "start_time", "end_time", "room"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = User.objects.filter(role=User.Role.TEACHER)


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "exam_type", "school_class", "subject", "date", "total_marks"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ["student", "month", "year", "amount_due", "amount_paid", "payment_date", "note"]
        widgets = {"payment_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = User.objects.filter(role=User.Role.STUDENT)


class FeeGenerateForm(forms.Form):
    from .models import MONTH_CHOICES
    school_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), label="শ্রেণি নির্বাচন করুন")
    month = forms.ChoiceField(choices=MONTH_CHOICES, label="মাস")
    year = forms.IntegerField(label="বছর", initial=2026)


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "content", "for_class", "pinned"]


class ExamResultInlineForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["marks_obtained", "remarks"]
