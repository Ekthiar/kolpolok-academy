from django.contrib import admin

from .models import Attendance, ClassRoutine, Exam, ExamResult, FeePayment, Notice, SchoolClass, Subject


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "order")
    ordering = ("order", "name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "school_class", "code")
    list_filter = ("school_class",)


@admin.register(ClassRoutine)
class ClassRoutineAdmin(admin.ModelAdmin):
    list_display = ("school_class", "subject", "teacher", "day", "start_time", "end_time", "room")
    list_filter = ("school_class", "day", "teacher")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "school_class", "subject", "date", "total_marks")
    list_filter = ("exam_type", "school_class", "subject")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "marks_obtained", "grade")
    list_filter = ("exam__school_class", "exam")
    search_fields = ("student__username", "student__first_name")


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "month", "year", "amount_due", "amount_paid", "status")
    list_filter = ("status", "month", "year")
    search_fields = ("student__username", "student__first_name")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "school_class", "date", "status")
    list_filter = ("school_class", "status", "date")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "for_class", "pinned", "created_at", "posted_by")
    list_filter = ("for_class", "pinned")
