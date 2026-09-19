from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "phone", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("অতিরিক্ত তথ্য", {"fields": ("role", "phone", "photo", "address")}),
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "designation", "specialization", "joining_date", "salary")
    search_fields = ("user__username", "user__first_name")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "school_class", "roll_number", "guardian_phone", "monthly_fee")
    list_filter = ("school_class",)
    search_fields = ("user__username", "user__first_name", "roll_number")
