from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from .decorators import admin_required, verifier_or_admin_required
from .models import Job, JobApplication, Inquiry, Profile, JobSeekerProfile, BackgroundVerification, VerifierProfile, BackgroundVerificationRequest, VERIFICATION_CATEGORIES, JobAlert, EmployerSubscription, ResumeUnlock
from .views import create_notification, search_jobs_for_query

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

#admin employers list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_employers_list(request):
    query = request.GET.get('q', '').strip()
    employers = Profile.objects.filter(is_employer=True).select_related(
        'user', 'user__subscription', 'user__subscription__plan'
    ).annotate(
        jobs_count=Count('user__posted_jobs', distinct=True),
        applicants_count=Count('user__posted_jobs__applications', distinct=True),
    ).order_by('-created_at')

    if query:
        employers = employers.filter(
            Q(company_name__icontains=query) | Q(user__email__icontains=query) | Q(user__username__icontains=query)
        )

    paginator = Paginator(employers, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/employers_list.html', {
        'active_tab': 'employers',
        'page_obj': page_obj,
        'query': query,
    })


#admin employer detail view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_employer_detail(request, employer_id):
    employer = get_object_or_404(Profile.objects.select_related(
        'user', 'user__subscription', 'user__subscription__plan'
    ), id=employer_id, is_employer=True)

    user = employer.user
    subscription = getattr(user, 'subscription', None)

    jobs = Job.objects.filter(posted_by=user).annotate(
        applicant_count=Count('applications', distinct=True),
    ).order_by('-posted_at')

    total_applicants = JobApplication.objects.filter(job__posted_by=user).count()
    resumes_unlocked = ResumeUnlock.objects.filter(employer=user).count()

    return render(request, 'core/admin_panel/employer_detail.html', {
        'active_tab': 'employers',
        'employer': employer,
        'user': user,
        'subscription': subscription,
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'total_applicants': total_applicants,
        'resumes_viewed': subscription.resumes_viewed_count if subscription else resumes_unlocked,
        'resumes_unlocked': resumes_unlocked,
    })


#admin job seekers list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_job_seekers_list(request):
    query = request.GET.get('q', '').strip()
    seekers = JobSeekerProfile.objects.select_related('user').order_by('-created_at')

    if query:
        seekers = seekers.filter(
            Q(full_name__icontains=query) | Q(user__email__icontains=query)
        )

    paginator = Paginator(seekers, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/job_seekers_list.html', {
        'active_tab': 'job_seekers',
        'page_obj': page_obj,
        'query': query,
    })


#admin subscriptions list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_subscriptions_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    subscriptions = EmployerSubscription.objects.select_related('user', 'plan', 'user__profile').order_by('-started_at')

    if query:
        subscriptions = subscriptions.filter(
            Q(user__profile__company_name__icontains=query) | Q(user__email__icontains=query)
        )

    subscriptions = list(subscriptions)
    if status == 'active':
        subscriptions = [s for s in subscriptions if s.is_active()]
    elif status == 'expired':
        subscriptions = [s for s in subscriptions if not s.is_active()]

    paginator = Paginator(subscriptions, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_panel/subscriptions_list.html', {
        'active_tab': 'subscriptions',
        'page_obj': page_obj,
        'query': query,
        'status': status,
    })
#admin user toggle active view  ------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Can't ban a superuser account.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    messages.success(request, f"{user.username} is now {'active' if user.is_active else 'banned'}.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

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


#admin job alerts list view ---------------------------------------------------------------------------------------------------------
@admin_required
def admin_job_alerts_list(request):
    alerts = JobAlert.objects.order_by('-created_at')
    paginator = Paginator(alerts, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Show how many relevant openings exist right now for each alert on the page.
    alerts_with_matches = []
    for alert in page_obj.object_list:
        matches = search_jobs_for_query(alert.job_query, limit=10)
        alerts_with_matches.append({'alert': alert, 'matches': matches})

    return render(request, 'core/admin_panel/job_alerts_list.html', {
        'active_tab': 'job_alerts',
        'page_obj': page_obj,
        'alerts_with_matches': alerts_with_matches,
    })


#admin job alert update status view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_job_alert_update_status(request, alert_id):
    alert = get_object_or_404(JobAlert, id=alert_id)
    new_status = request.POST.get('status')
    if new_status in dict(JobAlert.STATUS_CHOICES):
        alert.status = new_status
        alert.save(update_fields=['status'])
        messages.success(request, f"Job alert for {alert.full_name} marked as {new_status}.")
    return redirect('admin_job_alerts_list')


#admin job alert notify view ---------------------------------------------------------------------------------------------------------
@admin_required
@require_POST
def admin_job_alert_notify(request, alert_id):
    alert = get_object_or_404(JobAlert, id=alert_id)
    matches = search_jobs_for_query(alert.job_query, limit=10)

    if not matches:
        messages.info(request, f"No matching jobs posted yet for \"{alert.job_query}\". Try again later.")
        return redirect('admin_job_alerts_list')

    lines = []
    for job in matches:
        url = request.build_absolute_uri(reverse('job_detail', args=[job.id]))
        lines.append(f"- {job.job_title} at {job.company_name or 'a Deploynix employer'} ({job.location}) — {url}")

    message_body = (
        f"Hi {alert.full_name},\n\n"
        f"Good news! We now have job opening(s) matching what you asked our assistant about: \"{alert.job_query}\".\n\n"
        + "\n".join(lines) +
        "\n\nApply soon — roles fill up fast!\n\nBest,\nTeam Deploynix"
    )

    try:
        send_mail(
            subject=f"Job alert: {len(matches)} new opening(s) matching \"{alert.job_query}\"",
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[alert.email],
            fail_silently=False,
        )
        alert.status = 'Notified'
        alert.save(update_fields=['status'])
        messages.success(request, f"Email with {len(matches)} matching job(s) sent to {alert.email}.")
    except Exception as e:
        messages.error(request, f"Could not send the email right now: {e}")

    return redirect('admin_job_alerts_list')

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