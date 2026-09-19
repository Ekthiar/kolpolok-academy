from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required
from .forms import (
    StudentCreationForm,
    StudentProfileEditForm,
    TeacherCreationForm,
    TeacherProfileEditForm,
    UserEditForm,
)
from .models import User


@login_required
def profile_view(request):
    user = request.user
    profile_form = None
    if request.method == "POST":
        user_form = UserEditForm(request.POST, request.FILES, instance=user)
        if user.is_teacher_role() and hasattr(user, "teacher_profile"):
            profile_form = TeacherProfileEditForm(request.POST, instance=user.teacher_profile)
        elif user.is_student_role() and hasattr(user, "student_profile"):
            profile_form = StudentProfileEditForm(request.POST, instance=user.student_profile)

        valid = user_form.is_valid() and (profile_form is None or profile_form.is_valid())
        if valid:
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "প্রোফাইল সফলভাবে হালনাগাদ হয়েছে।")
            return redirect("profile")
    else:
        user_form = UserEditForm(instance=user)
        if user.is_teacher_role() and hasattr(user, "teacher_profile"):
            profile_form = TeacherProfileEditForm(instance=user.teacher_profile)
        elif user.is_student_role() and hasattr(user, "student_profile"):
            profile_form = StudentProfileEditForm(instance=user.student_profile)

    return render(request, "accounts/profile.html", {"user_form": user_form, "profile_form": profile_form})


@admin_required
def user_list(request):
    role_filter = request.GET.get("role", "")
    users = User.objects.all().order_by("role", "first_name")
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, "accounts/user_list.html", {"users": users, "role_filter": role_filter})


@admin_required
def add_teacher(request):
    if request.method == "POST":
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "নতুন শিক্ষক সফলভাবে যুক্ত হয়েছেন।")
            return redirect("user_list")
    else:
        form = TeacherCreationForm()
    return render(request, "accounts/add_user.html", {"form": form, "title": "নতুন শিক্ষক যুক্ত করুন"})


@admin_required
def add_student(request):
    if request.method == "POST":
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "নতুন শিক্ষার্থী সফলভাবে যুক্ত হয়েছে।")
            return redirect("user_list")
    else:
        form = StudentCreationForm()
    return render(request, "accounts/add_user.html", {"form": form, "title": "নতুন শিক্ষার্থী যুক্ত করুন"})


@admin_required
def edit_user(request, pk):
    target = get_object_or_404(User, pk=pk)
    profile_form = None
    if request.method == "POST":
        user_form = UserEditForm(request.POST, request.FILES, instance=target)
        if target.is_teacher_role() and hasattr(target, "teacher_profile"):
            profile_form = TeacherProfileEditForm(request.POST, instance=target.teacher_profile)
        elif target.is_student_role() and hasattr(target, "student_profile"):
            profile_form = StudentProfileEditForm(request.POST, instance=target.student_profile)

        valid = user_form.is_valid() and (profile_form is None or profile_form.is_valid())
        if valid:
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "ব্যবহারকারীর তথ্য হালনাগাদ হয়েছে।")
            return redirect("user_list")
    else:
        user_form = UserEditForm(instance=target)
        if target.is_teacher_role() and hasattr(target, "teacher_profile"):
            profile_form = TeacherProfileEditForm(instance=target.teacher_profile)
        elif target.is_student_role() and hasattr(target, "student_profile"):
            profile_form = StudentProfileEditForm(instance=target.student_profile)

    return render(request, "accounts/edit_user.html", {
        "user_form": user_form, "profile_form": profile_form, "target": target,
    })


@admin_required
def delete_user(request, pk):
    target = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        target.delete()
        messages.success(request, "ব্যবহারকারী মুছে ফেলা হয়েছে।")
        return redirect("user_list")
    return render(request, "accounts/confirm_delete.html", {"target": target})
