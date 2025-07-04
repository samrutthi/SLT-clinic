from django.db import models
from django.contrib.auth.models import User

# User Profile for assigning roles
class Profile(models.Model):
    ROLE_CHOICES = [
        ('receptionist', 'Receptionist'),
        ('therapist', 'Therapist'),
        ('clinical_supervisor', 'Clinical Supervisor'),
        ('case_supervisor', 'Case Supervisor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Patient Model
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    patient_id = models.CharField(max_length=10, unique=True, blank=True)
    is_first_time = models.BooleanField(default=True)
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    final_therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='final_therapist')
    case_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_supervisor')

    # ✅ New field for patient performance rating (given by case supervisor)
    rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.patient_id})"


# Pre-Assessment Report Model
class PreAssessmentReport(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_text = models.TextField()
    approved = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.patient.name}"


# ✅ NEW: Lesson Plan Model (submitted by therapist, reviewed by case supervisor)
class LessonPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    therapist = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)  # For case supervisor's feedback

    def __str__(self):
        return f"Lesson Plan for {self.patient.name} by {self.therapist.username}"


# ✅ NEW: Session Report Model (submitted by therapist for each session)
class SessionReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    therapist = models.ForeignKey(User, on_delete=models.CASCADE)
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session Report for {self.patient.name} by {self.therapist.username}"
