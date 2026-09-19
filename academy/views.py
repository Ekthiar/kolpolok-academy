from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required, student_required, teacher_required
from accounts.models import StudentProfile, User

from .forms import (
    ClassRoutineForm,
    ExamForm,
    ExamResultInlineForm,
    FeeGenerateForm,
    FeePaymentForm,
    NoticeForm,
    SchoolClassForm,
    SubjectForm,
)
from .models import (
    Attendance,
    ClassRoutine,
    Exam,
    ExamResult,
    FeePayment,
    Notice,
    SchoolClass,
    Subject,
)


def home(request):
    notices = Notice.objects.filter(for_class__isnull=True)[:5]
    classes = SchoolClass.objects.all()
    return render(request, "academy/home.html", {"notices": notices, "classes": classes})


@login_required
def dashboard(request):
    user = request.user
    context = {}
    if user.is_admin_role():
        context["total_students"] = User.objects.filter(role=User.Role.STUDENT).count()
        context["total_teachers"] = User.objects.filter(role=User.Role.TEACHER).count()
        context["total_classes"] = SchoolClass.objects.count()
        context["notices"] = Notice.objects.all()[:5]
        current_month = timezone.now().month
        current_year = timezone.now().year
        month_fees = FeePayment.objects.filter(month=current_month, year=current_year)
        context["due_amount_total"] = month_fees.aggregate(total=Sum("amount_due"))["total"] or 0
        context["paid_amount_total"] = month_fees.aggregate(total=Sum("amount_paid"))["total"] or 0
        return render(request, "academy/dashboard_admin.html", context)

    elif user.is_teacher_role():
        context["routines"] = ClassRoutine.objects.filter(teacher=user)
        context["exams_created"] = Exam.objects.filter(created_by=user)[:10]
        context["notices"] = Notice.objects.filter(Q(for_class__isnull=True) | Q(for_class__in=[
            r.school_class for r in context["routines"]
        ])).distinct()[:5]
        return render(request, "academy/dashboard_teacher.html", context)

    else:  # student
        profile = getattr(user, "student_profile", None)
        school_class = profile.school_class if profile else None
        context["profile"] = profile
        context["routines"] = ClassRoutine.objects.filter(school_class=school_class) if school_class else []
        context["recent_results"] = ExamResult.objects.filter(student=user)[:5]
        context["fees"] = FeePayment.objects.filter(student=user).order_by("-year", "-month")[:6]
        context["notices"] = Notice.objects.filter(
            Q(for_class__isnull=True) | Q(for_class=school_class)
        )[:5]
        return render(request, "academy/dashboard_student.html", context)


# ---------------- Class Routine ----------------

@login_required
def routine_list(request):
    user = request.user
    class_filter = request.GET.get("class", "")
    routines = ClassRoutine.objects.select_related("school_class", "subject", "teacher").all()

    if user.is_student_role():
        profile = getattr(user, "student_profile", None)
        if profile and profile.school_class:
            routines = routines.filter(school_class=profile.school_class)
        else:
            routines = routines.none()
    elif user.is_teacher_role():
        routines = routines.filter(teacher=user)

    if class_filter:
        routines = routines.filter(school_class_id=class_filter)

    classes = SchoolClass.objects.all()
    return render(request, "academy/routine_list.html", {
        "routines": routines, "classes": classes, "class_filter": class_filter,
    })


@admin_required
def routine_add(request):
    if request.method == "POST":
        form = ClassRoutineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ক্লাস রুটিন যুক্ত হয়েছে।")
            return redirect("routine_list")
    else:
        form = ClassRoutineForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "নতুন ক্লাস রুটিন"})


@admin_required
def routine_edit(request, pk):
    routine = get_object_or_404(ClassRoutine, pk=pk)
    if request.method == "POST":
        form = ClassRoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, "ক্লাস রুটিন হালনাগাদ হয়েছে।")
            return redirect("routine_list")
    else:
        form = ClassRoutineForm(instance=routine)
    return render(request, "academy/simple_form.html", {"form": form, "title": "ক্লাস রুটিন সম্পাদনা"})


@admin_required
def routine_delete(request, pk):
    routine = get_object_or_404(ClassRoutine, pk=pk)
    if request.method == "POST":
        routine.delete()
        messages.success(request, "ক্লাস রুটিন মুছে ফেলা হয়েছে।")
        return redirect("routine_list")
    return render(request, "academy/confirm_delete.html", {"object": routine, "back_url": "routine_list"})


# ---------------- Classes & Subjects ----------------

@admin_required
def class_list(request):
    classes = SchoolClass.objects.all()
    return render(request, "academy/class_list.html", {"classes": classes})


@admin_required
def class_add(request):
    if request.method == "POST":
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "নতুন শ্রেণি যুক্ত হয়েছে।")
            return redirect("class_list")
    else:
        form = SchoolClassForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "নতুন শ্রেণি যুক্ত করুন"})


@admin_required
def class_edit(request, pk):
    obj = get_object_or_404(SchoolClass, pk=pk)
    if request.method == "POST":
        form = SchoolClassForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "শ্রেণির তথ্য হালনাগাদ হয়েছে।")
            return redirect("class_list")
    else:
        form = SchoolClassForm(instance=obj)
    return render(request, "academy/simple_form.html", {"form": form, "title": "শ্রেণি সম্পাদনা"})


@admin_required
def class_delete(request, pk):
    obj = get_object_or_404(SchoolClass, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "শ্রেণি মুছে ফেলা হয়েছে।")
        return redirect("class_list")
    return render(request, "academy/confirm_delete.html", {"object": obj, "back_url": "class_list"})


@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related("school_class").all()
    return render(request, "academy/subject_list.html", {"subjects": subjects})


@admin_required
def subject_add(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "নতুন বিষয় যুক্ত হয়েছে।")
            return redirect("subject_list")
    else:
        form = SubjectForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "নতুন বিষয় যুক্ত করুন"})


@admin_required
def subject_edit(request, pk):
    obj = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "বিষয়ের তথ্য হালনাগাদ হয়েছে।")
            return redirect("subject_list")
    else:
        form = SubjectForm(instance=obj)
    return render(request, "academy/simple_form.html", {"form": form, "title": "বিষয় সম্পাদনা"})


@admin_required
def subject_delete(request, pk):
    obj = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "বিষয় মুছে ফেলা হয়েছে।")
        return redirect("subject_list")
    return render(request, "academy/confirm_delete.html", {"object": obj, "back_url": "subject_list"})


# ---------------- Exams & Results ----------------

@login_required
def exam_list(request):
    user = request.user
    exams = Exam.objects.select_related("school_class", "subject").all()
    if user.is_student_role():
        profile = getattr(user, "student_profile", None)
        exams = exams.filter(school_class=profile.school_class) if profile and profile.school_class else exams.none()
    elif user.is_teacher_role():
        taught_classes = ClassRoutine.objects.filter(teacher=user).values_list("school_class", flat=True)
        exams = exams.filter(school_class__in=taught_classes)
    return render(request, "academy/exam_list.html", {"exams": exams})


@teacher_required
def exam_add(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, "নতুন পরীক্ষা তৈরি হয়েছে। এখন ফলাফল যুক্ত করতে পারবেন।")
            return redirect("exam_result_entry", pk=exam.pk)
    else:
        form = ExamForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "নতুন পরীক্ষা তৈরি করুন"})


@admin_required
def exam_delete(request, pk):
    obj = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "পরীক্ষা মুছে ফেলা হয়েছে।")
        return redirect("exam_list")
    return render(request, "academy/confirm_delete.html", {"object": obj, "back_url": "exam_list"})


@teacher_required
def exam_result_entry(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    students = User.objects.filter(
        role=User.Role.STUDENT, student_profile__school_class=exam.school_class
    ).select_related("student_profile")

    existing_results = {r.student_id: r for r in ExamResult.objects.filter(exam=exam)}

    if request.method == "POST":
        for student in students:
            marks_raw = request.POST.get(f"marks_{student.id}", "").strip()
            remarks = request.POST.get(f"remarks_{student.id}", "").strip()
            if marks_raw == "":
                continue
            try:
                marks = float(marks_raw)
            except ValueError:
                continue
            result, _created = ExamResult.objects.update_or_create(
                exam=exam, student=student,
                defaults={"marks_obtained": marks, "remarks": remarks, "entered_by": request.user},
            )
        messages.success(request, "ফলাফল সংরক্ষণ করা হয়েছে।")
        return redirect("exam_list")

    rows = []
    for student in students:
        result = existing_results.get(student.id)
        rows.append({
            "student": student,
            "marks_obtained": result.marks_obtained if result else "",
            "remarks": result.remarks if result else "",
        })

    return render(request, "academy/exam_result_entry.html", {"exam": exam, "rows": rows})


@student_required
def my_results(request):
    results = ExamResult.objects.filter(student=request.user).select_related("exam", "exam__subject")
    exam_filter = request.GET.get("exam_type", "")
    if exam_filter:
        results = results.filter(exam__exam_type=exam_filter)
    return render(request, "academy/my_results.html", {"results": results, "exam_filter": exam_filter})


# ---------------- Fees ----------------

@student_required
def my_fees(request):
    fees = FeePayment.objects.filter(student=request.user).order_by("-year", "-month")
    return render(request, "academy/my_fees.html", {"fees": fees})


@admin_required
def fee_manage(request):
    fees = FeePayment.objects.select_related("student", "student__student_profile__school_class").all()
    status_filter = request.GET.get("status", "")
    if status_filter:
        fees = fees.filter(status=status_filter)
    return render(request, "academy/fee_manage.html", {"fees": fees, "status_filter": status_filter})


@admin_required
def fee_edit(request, pk):
    fee = get_object_or_404(FeePayment, pk=pk)
    if request.method == "POST":
        form = FeePaymentForm(request.POST, instance=fee)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user
            obj.save()
            messages.success(request, "বেতনের তথ্য হালনাগাদ হয়েছে।")
            return redirect("fee_manage")
    else:
        form = FeePaymentForm(instance=fee)
    return render(request, "academy/simple_form.html", {"form": form, "title": "বেতনের তথ্য সম্পাদনা"})


@admin_required
def fee_generate(request):
    if request.method == "POST":
        form = FeeGenerateForm(request.POST)
        if form.is_valid():
            school_class = form.cleaned_data["school_class"]
            month = form.cleaned_data["month"]
            year = form.cleaned_data["year"]
            profiles = StudentProfile.objects.filter(school_class=school_class)
            created_count = 0
            for profile in profiles:
                _obj, created = FeePayment.objects.get_or_create(
                    student=profile.user, month=month, year=year,
                    defaults={"amount_due": profile.monthly_fee, "updated_by": request.user},
                )
                if created:
                    created_count += 1
            messages.success(request, f"{created_count} জন শিক্ষার্থীর জন্য বেতনের তালিকা তৈরি হয়েছে।")
            return redirect("fee_manage")
    else:
        form = FeeGenerateForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "মাসিক বেতন তালিকা তৈরি করুন"})


# ---------------- Attendance ----------------

@teacher_required
def attendance_mark(request):
    school_classes = SchoolClass.objects.all()
    selected_class_id = request.POST.get("school_class") or request.GET.get("school_class")
    selected_date = request.POST.get("date") or request.GET.get("date") or timezone.now().date().isoformat()
    students = []
    existing = {}

    if selected_class_id:
        students = User.objects.filter(
            role=User.Role.STUDENT, student_profile__school_class_id=selected_class_id
        ).select_related("student_profile")
        existing = {
            a.student_id: a.status for a in Attendance.objects.filter(
                school_class_id=selected_class_id, date=selected_date
            )
        }

    if request.method == "POST" and selected_class_id:
        for student in students:
            status = request.POST.get(f"status_{student.id}", "PRESENT")
            Attendance.objects.update_or_create(
                student=student, date=selected_date,
                defaults={"school_class_id": selected_class_id, "status": status, "marked_by": request.user},
            )
        messages.success(request, "উপস্থিতি সংরক্ষণ করা হয়েছে।")
        return redirect(f"/attendance/mark/?school_class={selected_class_id}&date={selected_date}")

    return render(request, "academy/attendance_mark.html", {
        "school_classes": school_classes, "students": students, "existing": existing,
        "selected_class_id": selected_class_id, "selected_date": selected_date,
    })


@student_required
def my_attendance(request):
    all_records = Attendance.objects.filter(student=request.user).order_by("-date")
    total = all_records.count()
    present = all_records.filter(status=Attendance.Status.PRESENT).count()
    records = all_records[:60]
    return render(request, "academy/my_attendance.html", {
        "records": records, "total": total, "present": present,
    })


# ---------------- Notices ----------------

@login_required
def notice_list(request):
    user = request.user
    notices = Notice.objects.all()
    if user.is_student_role():
        profile = getattr(user, "student_profile", None)
        school_class = profile.school_class if profile else None
        notices = notices.filter(Q(for_class__isnull=True) | Q(for_class=school_class))
    return render(request, "academy/notice_list.html", {"notices": notices})


@teacher_required
def notice_add(request):
    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()
            messages.success(request, "নোটিশ প্রকাশিত হয়েছে।")
            return redirect("notice_list")
    else:
        form = NoticeForm()
    return render(request, "academy/simple_form.html", {"form": form, "title": "নতুন নোটিশ"})


@admin_required
def notice_delete(request, pk):
    obj = get_object_or_404(Notice, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "নোটিশ মুছে ফেলা হয়েছে।")
        return redirect("notice_list")
    return render(request, "academy/confirm_delete.html", {"object": obj, "back_url": "notice_list"})
