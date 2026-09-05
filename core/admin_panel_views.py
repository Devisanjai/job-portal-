from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from .decorators import admin_required, verifier_or_admin_required
from .models import Job, JobApplication, Inquiry, Profile, JobSeekerProfile, BackgroundVerification, VerifierProfile, BackgroundVerificationRequest, VERIFICATION_CATEGORIES
from .views import create_notification

#admin dashboard view -------------------------------------------------------------------------------------------------------
@admin_required
def admin_dashboard(request):
    total_job_seekers = JobSeekerProfile.objects.count()
    total_employers = Profile.objects.filter(is_employer=True).count()
    context = {
        'active_tab': 'dashboard',
        'total_job_seekers': total_job_seekers,
        'total_employers': total_employers,
        'total_users': total_job_seekers + total_employers,
        'total_jobs': Job.objects.count(),
        'pending_jobs': Job.objects.filter(approval_status='pending').count(),
        'total_applications': JobApplication.objects.count(),
        'open_inquiries': Inquiry.objects.exclude(status__in=['Closed', 'Replied']).count(),
    }
    return render(request, 'core/admin_panel/dashboard.html', context)

#admin jobs list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_jobs_list(request):
    jobs = Job.objects.select_related('posted_by').order_by('-posted_at')

    status = request.GET.get('status')
    if status in ('pending', 'approved', 'rejected'):
        jobs = jobs.filter(approval_status=status)

    paginator = Paginator(jobs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/jobs_list.html', {
        'active_tab': 'jobs',
        'page_obj': page_obj,
        'status': status,
    })

#job set status view -----------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_job_set_status(request, job_id, status):
    if status not in ('pending', 'approved', 'rejected'):
        messages.error(request, 'Invalid status.')
        return redirect('admin_jobs_list')
    job = get_object_or_404(Job, id=job_id)
    job.approval_status = status
    job.save(update_fields=['approval_status'])
    messages.success(request, f"'{job.job_title}' marked as {job.get_approval_status_display()}.")
    return redirect('admin_jobs_list')

#admin job detail view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    title = job.job_title
    job.delete()
    messages.success(request, f"Deleted job posting '{title}'.")
    return redirect('admin_jobs_list')

#admin user list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_users_list(request):
    role = request.GET.get('role', 'seekers')

    if role == 'employers':
            users = Profile.objects.filter(is_employer=True).select_related(
            'user', 'user__subscription', 'user__subscription__plan'
        ).order_by('-created_at')
    else:
        users = JobSeekerProfile.objects.select_related('user').order_by('-created_at')

    paginator = Paginator(users, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/users_list.html', {
        'active_tab': 'users',
        'page_obj': page_obj,
        'role': role,
    })

#admin user toggle active view  ------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Can't ban a superuser account.")
        return redirect('admin_users_list')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    messages.success(request, f"{user.username} is now {'active' if user.is_active else 'banned'}.")
    return redirect('admin_users_list')

#admin inquiries list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_inquiries_list(request):
    inquiries = Inquiry.objects.order_by('-created_at')
    paginator = Paginator(inquiries, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/inquiries_list.html', {
        'active_tab': 'inquiries',
        'page_obj': page_obj,
    })

#admin inquiry update status view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_inquiry_update_status(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    new_status = request.POST.get('status')
    if new_status in dict(Inquiry.STATUS_CHOICES):
        inquiry.status = new_status
        inquiry.save(update_fields=['status'])
        messages.success(request, "Inquiry status updated.")
    return redirect('admin_inquiries_list')

#admin verification list view ---------------------------------------------------------------------------------------------------------
@verifier_or_admin_required
def admin_verifications_list(request):
    requests_qs = BackgroundVerificationRequest.objects.select_related(
        'job_application', 'job_application__job', 'job_application__job_seeker_profile', 'verified_by'
    ).order_by('-has_new_documents', '-updated_at')

    status = request.GET.get('status')
    if status in dict(BackgroundVerificationRequest.STATUS_CHOICES):
        requests_qs = requests_qs.filter(status=status)

    paginator = Paginator(requests_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/verifications_list.html', {
        'active_tab': 'verifications',
        'page_obj': page_obj,
        'status': status,
    })

#admin verification detail view ---------------------------------------------------------------------------------------------------------
@verifier_or_admin_required
def admin_verification_detail(request, verification_id):
    verification_request = get_object_or_404(BackgroundVerificationRequest, id=verification_id)
    profile = verification_request.job_application.job_seeker_profile
    documents = profile.verification_documents.all().order_by('document_type') if profile else []

    if request.method == 'POST':
        new_status = request.POST.get('status')
        criminal_status = request.POST.get('criminal_check_status')
        notes = request.POST.get('internal_notes', '')
        employer_report = request.POST.get('employer_report', '')

        if new_status in dict(BackgroundVerificationRequest.STATUS_CHOICES):
            verification_request.status = new_status
            verification_request.internal_notes = notes
            verification_request.employer_report = employer_report
            verification_request.has_new_documents = False
            if criminal_status in dict(BackgroundVerificationRequest.CRIMINAL_CHECK_CHOICES):
                verification_request.criminal_check_status = criminal_status
            if new_status in ('verified', 'rejected', 'flagged'):
                verification_request.verified_by = request.user
                verification_request.verified_at = timezone.now()
            verification_request.save()
            messages.success(request, f"Status updated to {verification_request.get_status_display()}.")
            return redirect('admin_verifications_list')

    return render(request, 'core/admin_panel/verification_detail.html', {
        'active_tab': 'verifications',
        'verification': verification_request,
        'documents': documents,
        'categories': VERIFICATION_CATEGORIES,
    })

#admin verifiers list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_verifiers_list(request):
    verifiers = VerifierProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'core/admin_panel/verifiers_list.html', {
        'active_tab': 'verifiers',
        'verifiers': verifiers,
    })

#admin verifier create view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_verifier_create(request):
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    if not username or not password:
        messages.error(request, "Username and password are required.")
        return redirect('admin_verifiers_list')

    if User.objects.filter(username=username).exists():
        messages.error(request, f"Username '{username}' is already taken.")
        return redirect('admin_verifiers_list')

    user = User.objects.create_user(username=username, email=email, password=password)
    VerifierProfile.objects.create(user=user, created_by=request.user)
    messages.success(request, f"Verifier account '{username}' created.")
    return redirect('admin_verifiers_list')

#admin verifier toggle active view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_verifier_toggle_active(request, verifier_id):
    verifier = get_object_or_404(VerifierProfile, id=verifier_id)
    verifier.is_active_verifier = not verifier.is_active_verifier
    verifier.save(update_fields=['is_active_verifier'])
    verifier.user.is_active = verifier.is_active_verifier
    verifier.user.save(update_fields=['is_active'])
    messages.success(request, f"{verifier.user.username} is now {'active' if verifier.is_active_verifier else 'disabled'}.")
    return redirect('admin_verifiers_list')

#admin request more documents view ---------------------------------------------------------------------------------------------------------
@verifier_or_admin_required
@require_POST
def admin_request_more_documents(request, verification_id):
    verification_request = get_object_or_404(BackgroundVerificationRequest, id=verification_id)
    message_text = request.POST.get('message', '').strip()

    if not message_text:
        messages.error(request, 'Please write a message describing what is needed.')
        return redirect('admin_verification_detail', verification_id=verification_id)

    verification_request.additional_info_requested = message_text
    verification_request.save(update_fields=['additional_info_requested'])

    profile = verification_request.job_application.job_seeker_profile
    if profile:
        create_notification(
            user=profile.user,
            message=f"Additional documents needed for your verification: {message_text}",
            notification_type='general',
            link=reverse('complete_verification', args=[verification_request.id]),
        )
    messages.success(request, 'Candidate notified.')
    return redirect('admin_verification_detail', verification_id=verification_id)

#admin verification accept view ---------------------------------------------------------------------------------------------------------
@verifier_or_admin_required
@require_POST
def admin_verification_accept(request, verification_id):
    verification_request = get_object_or_404(BackgroundVerificationRequest, id=verification_id)
    verification_request.status = 'in_progress'
    verification_request.save(update_fields=['status'])
    messages.success(request, 'Verification accepted and marked as Under Process.')
    return redirect('admin_verification_detail', verification_id=verification_id)