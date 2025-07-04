from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from .models import Profile, Patient, PreAssessmentReport, LessonPlan, SessionReport
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return HttpResponse("Welcome to Speech Therapy Project!")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)

            if profile.role == 'receptionist':
                return redirect('receptionist_dashboard')
            elif profile.role == 'therapist':
                return redirect('therapist_dashboard')
            elif profile.role == 'clinical_supervisor':
                return redirect('clinical_supervisor_dashboard')
            elif profile.role == 'case_supervisor':
                return redirect('case_supervisor_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def receptionist_dashboard(request):
    therapists = User.objects.filter(
        profile__role='therapist'
    ).annotate(
        patient_count=Count('patient')
    ).filter(patient_count__lt=5)

    patients = Patient.objects.all().order_by('-created_at')

    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        gender = request.POST['gender']
        phone = request.POST['phone']
        therapist_id = request.POST['therapist']
        therapist = User.objects.get(id=therapist_id)

        new_patient = Patient.objects.create(
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            therapist=therapist,
        )

        new_patient.patient_id = f"PT{1000 + new_patient.id}"
        new_patient.save()

        messages.success(request, f"Patient {new_patient.name} added successfully.")
        return redirect('receptionist_dashboard')

    return render(request, 'receptionist_dashboard.html', {
        'therapists': therapists,
        'patients': patients
    })

@login_required
def therapist_dashboard(request):
    user = request.user

    pre_assessment_patients = Patient.objects.filter(
        therapist=user,
        preassessmentreport__isnull=True
    )

    final_therapy_patients = Patient.objects.filter(final_therapist=user)
    reports = PreAssessmentReport.objects.filter(therapist=user)
    lesson_plans = LessonPlan.objects.filter(therapist=user)
    session_reports = SessionReport.objects.filter(therapist=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'pre_assessment':
            patient_id = request.POST.get('patient_id')
            if not patient_id:
                messages.error(request, "No patient selected.")
                return redirect('therapist_dashboard')
            report_text = request.POST.get('report_text')
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                messages.error(request, "Patient not found.")
                return redirect('therapist_dashboard')

            if patient.therapist != user:
                messages.error(request, "You are not assigned to this patient.")
                return redirect('therapist_dashboard')

            if PreAssessmentReport.objects.filter(patient=patient).exists():
                messages.warning(request, "Report already submitted for this patient.")
                return redirect('therapist_dashboard')

            PreAssessmentReport.objects.create(
                patient=patient,
                therapist=user,
                report_text=report_text
            )
            messages.success(request, "Pre-assessment report submitted.")
            return redirect('therapist_dashboard')

        elif form_type == 'lesson_plan':
            patient_id = request.POST.get('patient_id')
            if not patient_id:
               messages.error(request, "No patient selected.")
               return redirect('therapist_dashboard')
            plan_text = request.POST.get('plan_text')

            patient = get_object_or_404(Patient, id=patient_id)
            LessonPlan.objects.create(
                patient=patient,
                therapist=user,
                plan_text=plan_text
            )
            messages.success(request, "Lesson plan submitted successfully.")
            return redirect('therapist_dashboard')

        elif form_type == 'session_report':
            patient_id = request.POST.get('patient_id')
            if not patient_id:
               messages.error(request, "No patient selected.")
               return redirect('therapist_dashboard')
            report_text = request.POST.get('report_text')

            patient = get_object_or_404(Patient, id=patient_id)
            SessionReport.objects.create(
                patient=patient,
                therapist=user,
                report_text=report_text
            )
            messages.success(request, "Session report submitted successfully.")
            return redirect('therapist_dashboard')

    return render(request, 'therapist_dashboard.html', {
        'pre_assessment_patients': pre_assessment_patients,
        'final_therapy_patients': final_therapy_patients,
        'reports': reports,
        'lesson_plans': lesson_plans,
        'session_reports': session_reports
    })
@login_required
def clinical_supervisor_dashboard(request):
    reports_pending = PreAssessmentReport.objects.filter(
        Q(approved=False) & (Q(feedback__isnull=True) | Q(feedback=''))
    )

    pending_reports = Patient.objects.filter(
        therapist__isnull=False,
        preassessmentreport__isnull=True
    )

    if request.method == 'POST':
        if 'report_id' in request.POST:
            report_id = request.POST.get('report_id')
            action = request.POST.get('action')
            feedback = request.POST.get('feedback', '')
            report = get_object_or_404(PreAssessmentReport, id=report_id)

            report.approved = True if action == 'approve' else False
            report.feedback = feedback
            report.save()

        elif 'allocate' in request.POST:
            approved_reports = PreAssessmentReport.objects.filter(approved=True)
            patients_to_allocate = Patient.objects.filter(
                preassessmentreport__in=approved_reports,
                final_therapist__isnull=True
            )

            for patient in patients_to_allocate:
                therapist_id = request.POST.get(f'therapist_{patient.id}')
                case_supervisor_id = request.POST.get(f'case_supervisor_{patient.id}')

                if therapist_id and case_supervisor_id:
                    patient.final_therapist = User.objects.get(id=therapist_id)
                    patient.case_supervisor = User.objects.get(id=case_supervisor_id)
                    patient.save()

        return redirect('clinical_supervisor_dashboard')

    approved_reports = PreAssessmentReport.objects.filter(approved=True)
    patients_to_allocate = Patient.objects.filter(
        preassessmentreport__in=approved_reports,
        final_therapist__isnull=True
    )
    case_supervisors = User.objects.filter(profile__role='case_supervisor')
    therapists = User.objects.filter(profile__role='therapist')

    summary = {
        'total_patients': Patient.objects.count(),
        'pending_reports': pending_reports.count(),
        'approved_reports': approved_reports.count(),
        'therapist_count': therapists.count(),
    }

    return render(request, 'clinical_supervisor_dashboard.html', {
        'reports_pending': reports_pending,
        'pending_reports': pending_reports,
        'patients_to_allocate': patients_to_allocate,
        'case_supervisors': case_supervisors,
        'therapists': therapists,
        'summary': summary,
    })

@login_required
def case_supervisor_dashboard(request):
    user = request.user

    # Get patients supervised by this case supervisor
    supervised_patients = Patient.objects.filter(case_supervisor=user)

    # Filter only lesson plans with no feedback
    lesson_plans = LessonPlan.objects.filter(patient__in=supervised_patients, feedback__isnull=True)

    # All session reports for supervised patients
    session_reports = SessionReport.objects.filter(patient__in=supervised_patients)

    # Patients without a rating yet
    patients_to_rate = supervised_patients.filter(rating__isnull=True)

    # Therapists under this case supervisor (based on patients)
    therapists = User.objects.filter(
        profile__role='therapist',
        final_therapist__in=supervised_patients
    ).distinct()

    if request.method == 'POST':
        if 'submit_feedback' in request.POST:
            for plan in lesson_plans:
                feedback = request.POST.get(f'feedback_{plan.id}')
                if feedback:
                    plan.feedback = feedback
                    plan.save()

        if 'submit_rating' in request.POST:
            for patient in patients_to_rate:
                rating = request.POST.get(f'rating_{patient.id}')
                if rating:
                    patient.rating = int(rating)
                    patient.save()

        messages.success(request, "Feedback and ratings updated successfully.")
        return redirect('case_supervisor_dashboard')

    return render(request, 'case_supervisor_dashboard.html', {
        'supervised_patients': supervised_patients,
        'lesson_plans': lesson_plans,
        'session_reports': session_reports,
        'patients_to_rate': patients_to_rate,
        'therapists': therapists,
    })