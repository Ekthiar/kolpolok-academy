from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Class routine
    path('routine/', views.routine_list, name='routine_list'),
    path('routine/add/', views.routine_add, name='routine_add'),
    path('routine/<int:pk>/edit/', views.routine_edit, name='routine_edit'),
    path('routine/<int:pk>/delete/', views.routine_delete, name='routine_delete'),

    # Classes & Subjects
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.class_add, name='class_add'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Exams & Results
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.exam_add, name='exam_add'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('exams/<int:pk>/results/', views.exam_result_entry, name='exam_result_entry'),
    path('results/my/', views.my_results, name='my_results'),

    # Fees
    path('fees/my/', views.my_fees, name='my_fees'),
    path('fees/manage/', views.fee_manage, name='fee_manage'),
    path('fees/<int:pk>/edit/', views.fee_edit, name='fee_edit'),
    path('fees/generate/', views.fee_generate, name='fee_generate'),

    # Attendance
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('attendance/my/', views.my_attendance, name='my_attendance'),

    # Notices
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/add/', views.notice_add, name='notice_add'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
]
