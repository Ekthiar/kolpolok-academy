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
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        label="বিষয়সমূহ (একাধিক বিষয় বাছাই করুন)",
        widget=forms.CheckboxSelectMultiple,
        help_text="যে যে বিষয়ে পরীক্ষা হবে তার পাশে টিক দিন। প্রতিটি বিষয়ের জন্য আলাদা পরীক্ষা তৈরি হবে।",
    )

    class Meta:
        model = Exam
        fields = ["name", "exam_type", "school_class", "date", "total_marks"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subjects"].queryset = Subject.objects.select_related("school_class").order_by(
            "school_class__order", "name"
        )
        # Field order: put subjects right after school_class
        self.order_fields(["name", "exam_type", "school_class", "subjects", "date", "total_marks"])


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
