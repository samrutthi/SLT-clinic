
from django.contrib import admin
from .models import (
    Profile, Patient, PreAssessmentReport,
    LessonPlan, SessionReport
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    search_fields = ('user__username', 'role')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'patient_id', 'gender', 'age', 'phone',
        'therapist', 'final_therapist', 'case_supervisor',
        'is_first_time', 'created_at'
    )
    search_fields = ('name', 'patient_id', 'phone')
    list_filter = ('gender', 'is_first_time', 'therapist', 'final_therapist', 'case_supervisor')

@admin.register(PreAssessmentReport)
class PreAssessmentReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'therapist', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('patient__name', 'therapist__username')

@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ('patient', 'therapist', 'created_at', 'feedback')
    search_fields = ('patient__name', 'therapist__username')
    list_filter = ('created_at',)

@admin.register(SessionReport)
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'therapist', 'created_at')
    search_fields = ('patient__name', 'therapist__username')
    list_filter = ('created_at',)
