from django.conf import settings
from django.db import models
from django.utils import timezone

MONTH_CHOICES = [
    (1, "জানুয়ারি"), (2, "ফেব্রুয়ারি"), (3, "মার্চ"), (4, "এপ্রিল"),
    (5, "মে"), (6, "জুন"), (7, "জুলাই"), (8, "আগস্ট"),
    (9, "সেপ্টেম্বর"), (10, "অক্টোবর"), (11, "নভেম্বর"), (12, "ডিসেম্বর"),
]

DAY_CHOICES = [
    ("SAT", "শনিবার"), ("SUN", "রবিবার"), ("MON", "সোমবার"),
    ("TUE", "মঙ্গলবার"), ("WED", "বুধবার"), ("THU", "বৃহস্পতিবার"), ("FRI", "শুক্রবার"),
]


class SchoolClass(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="যেমনঃ ষষ্ঠ শ্রেণি, SSC ব্যাচ")
    section = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="তালিকায় ক্রম নির্ধারণের জন্য")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name}{(' - ' + self.section) if self.section else ''}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ("name", "school_class")

    def __str__(self):
        return f"{self.name} ({self.school_class})"


class ClassRoutine(models.Model):
    """Weekly class schedule entry."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="routines")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="routines")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="teaching_routines", limit_choices_to={"role": "TEACHER"}
    )
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.school_class} - {self.subject} - {self.get_day_display()} ({self.start_time}-{self.end_time})"


class Exam(models.Model):
    class ExamType(models.TextChoices):
        WEEKLY = "WEEKLY", "সাপ্তাহিক পরীক্ষা"
        MONTHLY = "MONTHLY", "মাসিক পরীক্ষা"
        MODEL = "MODEL", "মডেল টেস্ট"
        FINAL = "FINAL", "বার্ষিক/চূড়ান্ত পরীক্ষা"

    name = models.CharField(max_length=150)
    exam_type = models.CharField(max_length=10, choices=ExamType.choices, default=ExamType.WEEKLY)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exams")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    date = models.DateField(default=timezone.now)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="exams_created"
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} - {self.school_class} - {self.subject}"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_results",
        limit_choices_to={"role": "STUDENT"}
    )
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="results_entered"
    )
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "student")
        ordering = ["-exam__date"]

    @property
    def percentage(self):
        if self.exam.total_marks:
            return round((self.marks_obtained / self.exam.total_marks) * 100, 2)
        return 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 80:
            return "A+"
        elif p >= 70:
            return "A"
        elif p >= 60:
            return "A-"
        elif p >= 50:
            return "B"
        elif p >= 40:
            return "C"
        elif p >= 33:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"


class FeePayment(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "পরিশোধিত"
        DUE = "DUE", "বকেয়া"
        PARTIAL = "PARTIAL", "আংশিক পরিশোধিত"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fee_payments",
        limit_choices_to={"role": "STUDENT"}
    )
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=timezone.now().year)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DUE)
    note = models.CharField(max_length=255, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="fees_updated"
    )

    class Meta:
        unique_together = ("student", "month", "year")
        ordering = ["-year", "-month"]

    @property
    def due_amount(self):
        return self.amount_due - self.amount_paid

    def save(self, *args, **kwargs):
        if self.amount_paid <= 0:
            self.status = self.Status.DUE
        elif self.amount_paid >= self.amount_due:
            self.status = self.Status.PAID
        else:
            self.status = self.Status.PARTIAL
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.get_month_display()}/{self.year} - {self.status}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "উপস্থিত"
        ABSENT = "ABSENT", "অনুপস্থিত"
        LATE = "LATE", "বিলম্বে উপস্থিত"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances",
        limit_choices_to={"role": "STUDENT"}
    )
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_marked"
    )

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="notices_posted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    for_class = models.ForeignKey(
        SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name="notices",
        help_text="নির্দিষ্ট শ্রেণির জন্য না হলে খালি রাখুন (সবার জন্য প্রযোজ্য হবে)"
    )
    pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pinned", "-created_at"]

    def __str__(self):
        return self.title
