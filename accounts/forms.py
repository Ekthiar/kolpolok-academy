from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import StudentProfile, TeacherProfile, User


class TeacherCreationForm(UserCreationForm):
    first_name = forms.CharField(label="নাম", max_length=150)
    email = forms.EmailField(label="ইমেইল", required=False)
    phone = forms.CharField(label="ফোন নম্বর", max_length=20, required=False)
    designation = forms.CharField(label="পদবি", max_length=100, required=False)
    specialization = forms.CharField(label="বিষয়/স্পেশালাইজেশন", max_length=150, required=False)
    joining_date = forms.DateField(label="যোগদানের তারিখ", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    salary = forms.DecimalField(label="বেতন (মাসিক)", required=False, initial=0)

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "phone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.email = self.cleaned_data.get("email", "")
        user.phone = self.cleaned_data.get("phone", "")
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                designation=self.cleaned_data.get("designation", ""),
                specialization=self.cleaned_data.get("specialization", ""),
                joining_date=self.cleaned_data.get("joining_date"),
                salary=self.cleaned_data.get("salary") or 0,
            )
        return user


class StudentCreationForm(UserCreationForm):
    first_name = forms.CharField(label="নাম", max_length=150)
    email = forms.EmailField(label="ইমেইল", required=False)
    phone = forms.CharField(label="ফোন নম্বর", max_length=20, required=False)
    school_class = forms.ModelChoiceField(label="শ্রেণি", queryset=None, required=True)
    roll_number = forms.CharField(label="রোল নম্বর", max_length=20, required=False)
    guardian_name = forms.CharField(label="অভিভাবকের নাম", max_length=150, required=False)
    guardian_phone = forms.CharField(label="অভিভাবকের ফোন", max_length=20, required=False)
    admission_date = forms.DateField(label="ভর্তির তারিখ", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    monthly_fee = forms.DecimalField(label="মাসিক বেতন", required=False, initial=0)

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academy.models import SchoolClass
        self.fields["school_class"].queryset = SchoolClass.objects.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.email = self.cleaned_data.get("email", "")
        user.phone = self.cleaned_data.get("phone", "")
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                school_class=self.cleaned_data.get("school_class"),
                roll_number=self.cleaned_data.get("roll_number", ""),
                guardian_name=self.cleaned_data.get("guardian_name", ""),
                guardian_phone=self.cleaned_data.get("guardian_phone", ""),
                admission_date=self.cleaned_data.get("admission_date"),
                monthly_fee=self.cleaned_data.get("monthly_fee") or 0,
            )
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address", "photo"]


class TeacherProfileEditForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ["designation", "specialization", "joining_date", "salary"]
        widgets = {"joining_date": forms.DateInput(attrs={"type": "date"})}


class StudentProfileEditForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["school_class", "roll_number", "guardian_name", "guardian_phone", "admission_date", "monthly_fee"]
        widgets = {"admission_date": forms.DateInput(attrs={"type": "date"})}
