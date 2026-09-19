import datetime

from django.core.management.base import BaseCommand

from accounts.models import StudentProfile, TeacherProfile, User
from academy.models import (
    Attendance,
    ClassRoutine,
    Exam,
    ExamResult,
    FeePayment,
    Notice,
    SchoolClass,
    Subject,
)


class Command(BaseCommand):
    help = "Kolpolok Academy অ্যাপের জন্য নমুনা (demo) ডেটা তৈরি করে।"

    def handle(self, *args, **options):
        self.stdout.write("নমুনা ডেটা তৈরি করা হচ্ছে...")

        # --- Admin ---
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", password="admin12345", first_name="একাডেমি",
                last_name="অ্যাডমিন", role=User.Role.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS("সুপারইউজার 'admin' তৈরি হয়েছে (পাসওয়ার্ড: admin12345)"))

        # --- Classes ---
        class_names = [("ষষ্ঠ শ্রেণি", 6), ("সপ্তম শ্রেণি", 7), ("অষ্টম শ্রেণি", 8), ("নবম শ্রেণি", 9), ("এসএসসি ব্যাচ", 10)]
        classes = {}
        for name, order in class_names:
            obj, _ = SchoolClass.objects.get_or_create(name=name, defaults={"order": order})
            classes[name] = obj

        # --- Subjects ---
        subject_names = ["বাংলা", "ইংরেজি", "গণিত", "বিজ্ঞান", "সমাজবিজ্ঞান"]
        for cname, cobj in classes.items():
            for sname in subject_names:
                Subject.objects.get_or_create(name=sname, school_class=cobj)

        # --- Teachers ---
        teacher_data = [
            ("rahim_sir", "রহিম", "উদ্দিন", "গণিত"),
            ("karim_sir", "করিম", "হোসেন", "বিজ্ঞান"),
            ("nasrin_ma'am", "নাসরিন", "আক্তার", "ইংরেজি"),
        ]
        teachers = []
        for username, fname, lname, spec in teacher_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": fname, "last_name": lname, "role": User.Role.TEACHER,
                    "phone": "017XXXXXXXX",
                },
            )
            if created:
                user.set_password("teacher12345")
                user.save()
                TeacherProfile.objects.create(
                    user=user, designation="সহকারী শিক্ষক", specialization=spec,
                    joining_date=datetime.date(2024, 1, 1), salary=20000,
                )
            teachers.append(user)

        # --- Students ---
        student_data = [
            ("student1", "আনিকা", "তাসনিম", "ষষ্ঠ শ্রেণি", "01"),
            ("student2", "ফারহান", "আহমেদ", "সপ্তম শ্রেণি", "02"),
            ("student3", "সাদিয়া", "ইসলাম", "অষ্টম শ্রেণি", "03"),
            ("student4", "তানভীর", "রহমান", "নবম শ্রেণি", "04"),
            ("student5", "মাহি", "চৌধুরী", "এসএসসি ব্যাচ", "05"),
        ]
        students = []
        for username, fname, lname, cname, roll in student_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": fname, "last_name": lname, "role": User.Role.STUDENT},
            )
            if created:
                user.set_password("student12345")
                user.save()
                StudentProfile.objects.create(
                    user=user, school_class=classes[cname], roll_number=roll,
                    guardian_name=f"{fname} এর অভিভাবক", guardian_phone="018XXXXXXXX",
                    admission_date=datetime.date(2025, 1, 1), monthly_fee=1500,
                )
            students.append(user)

        # --- Class Routine ---
        days = ["SAT", "SUN", "MON", "TUE", "WED"]
        for i, (cname, cobj) in enumerate(classes.items()):
            subjects = list(Subject.objects.filter(school_class=cobj))
            for j, day in enumerate(days[:3]):
                ClassRoutine.objects.get_or_create(
                    school_class=cobj, subject=subjects[j % len(subjects)],
                    teacher=teachers[j % len(teachers)], day=day,
                    start_time=datetime.time(16 + j, 0), end_time=datetime.time(17 + j, 0),
                    defaults={"room": f"রুম-{i + 1}"},
                )

        # --- Sample Exam + Results ---
        for cname, cobj in classes.items():
            subject = Subject.objects.filter(school_class=cobj).first()
            exam, _ = Exam.objects.get_or_create(
                name=f"{cname} - সাপ্তাহিক পরীক্ষা ১", exam_type=Exam.ExamType.WEEKLY,
                school_class=cobj, subject=subject,
                defaults={"date": datetime.date.today(), "total_marks": 50},
            )
            for student in students:
                profile = getattr(student, "student_profile", None)
                if profile and profile.school_class_id == cobj.id:
                    ExamResult.objects.get_or_create(
                        exam=exam, student=student, defaults={"marks_obtained": 38}
                    )

        # --- Sample Fee ---
        today = datetime.date.today()
        for student in students:
            profile = getattr(student, "student_profile", None)
            if profile:
                FeePayment.objects.get_or_create(
                    student=student, month=today.month, year=today.year,
                    defaults={"amount_due": profile.monthly_fee, "amount_paid": 0},
                )

        # --- Sample Attendance ---
        for student in students:
            profile = getattr(student, "student_profile", None)
            if profile and profile.school_class:
                Attendance.objects.get_or_create(
                    student=student, date=today,
                    defaults={"school_class": profile.school_class, "status": Attendance.Status.PRESENT},
                )

        # --- Notice ---
        Notice.objects.get_or_create(
            title="স্বাগতম!",
            defaults={
                "content": "কল্পলোক একাডেমির নতুন ওয়েব পোর্টালে সবাইকে স্বাগতম। এখানে ক্লাস রুটিন, রেজাল্ট ও বেতনের তথ্য পাওয়া যাবে।",
                "pinned": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("নমুনা ডেটা তৈরি সম্পন্ন হয়েছে।"))
        self.stdout.write("লগইন তথ্য:")
        self.stdout.write("  Admin    -> admin / admin12345")
        self.stdout.write("  Teacher  -> rahim_sir / teacher12345")
        self.stdout.write("  Student  -> student1 / student12345")
