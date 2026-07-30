from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator

import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Job, JobApplication, Inquiry, Interview,
    JobSeekerProfile, SubscriptionPlan, EmployerSubscription, ResumeUnlock, Profile,
)
from .forms import (
    SignUpForm, EmployerLoginForm, JobSeekerLoginForm, JobPostForm,
    JobApplicationForm, EmployerAddCandidateForm, InterviewForm, JobSeekerProfileForm,
)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

SERVICES_DATA = {
    'premium-membership': {
        'title': 'Premium Membership',
        'description': 'Increase Your Chances of Getting Shortlisted',
        'image': 'member.jpg',
        'details': 'With Premium Membership, your profile gets priority visibility to recruiters, early access to job postings, and personalized career guidance to help you stand out from other applicants.',
    },
    'placement-paper': {
        'title': 'Placement Paper',
        'description': 'Practice & improve your skills',
        'image': 'member1.png',
        'details': 'Access a curated library of previous placement papers and mock tests from top companies to sharpen your technical and aptitude skills before your next interview.',
    },
    'interview-grooming': {
        'title': 'Interview Grooming',
        'description': 'Attend interviews confidently',
        'image': 'member2.png',
        'details': 'Get one-on-one mock interview sessions, feedback from industry experts, and tips on body language, communication, and technical presentation to walk into your interview with confidence.',
    },
}


def service_detail(request, slug):
    service = SERVICES_DATA.get(slug)
    return render(request, 'core/service_detail.html', {'service': service, 'slug': slug})


def home(request):
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    searched = bool(query or location)
    if searched:
        jobs = Job.objects.all().order_by('-posted_at')
        if query:
            jobs = jobs.filter(Q(job_title__icontains=query) | Q(skills_required__icontains=query))
        if location:
            jobs = jobs.filter(location__icontains=location)
        jobs = jobs[:12]
    else:
        jobs = Job.objects.none()

    return render(request, 'core/home.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'searched': searched,
    })


def job_vacancies(request):
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    jobs = Job.objects.all().order_by('-posted_at')

    if query:
        jobs = jobs.filter(Q(job_title__icontains=query) | Q(skills_required__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)

    return render(request, 'core/job_vacancies.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'searched': bool(query or location),
    })



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            free_plan = SubscriptionPlan.objects.filter(name='Free').first()
            if free_plan:
                EmployerSubscription.objects.create(
                    user=user,
                    plan=free_plan,
                    expires_at=timezone.now() + timedelta(days=free_plan.duration_days),
                )

            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


def employer_login(request):
    if request.method == 'POST':
        form = EmployerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            company_name = form.cleaned_data['company_name']
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'No account found with that email.')
                return render(request, 'core/employer_login.html', {'form': form})

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={'is_employer': True, 'company_name': company_name}
                )
                if not created and company_name:
                    profile.company_name = company_name
                    profile.save()

                return redirect('employer_dashboard')
            else:
                messages.error(request, 'Incorrect password.')
    else:
        # Clear accumulated unread messages from session when loading the login page
        storage = get_messages(request)
        for _ in storage:
            pass

        form = EmployerLoginForm()

    return render(request, 'core/employer_login.html', {'form': form})
def employer_dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user)
    applications = JobApplication.objects.filter(job__posted_by=request.user).order_by('-applied_at')
    interviews = Interview.objects.filter(application__job__posted_by=request.user).order_by('scheduled_at')
    upcoming_interviews = interviews.filter(status='scheduled')[:5]

    # Paginate recent candidates (5 per page)
    paginator = Paginator(applications, 5)
    page_number = request.GET.get('page', 1)
    recent_candidates = paginator.get_page(page_number)

    context = {
        'jobs_posted_count': jobs.count(),
        'applicants_total': applications.count(),
        'applicants_pending': applications.filter(status='applied').count(),
        'interview_list': interviews.count(),
        'inquiries_total': 93,
        'inquiries_unread': 93,
        'upcoming_interviews': upcoming_interviews,
        'recent_candidates': recent_candidates,
    }
    return render(request, 'core/employer_dashboard.html', context)

@login_required(login_url='employer_login')
def company_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'is_employer': True}
    )

    if request.method == 'POST':
        profile.company_name = request.POST.get('company_name', '')
        profile.phone = request.POST.get('phone', '')
        profile.about = request.POST.get('about', '')
        profile.industry = request.POST.get('industry', '')
        profile.website = request.POST.get('website', '')
        profile.company_size = request.POST.get('company_size', '')
        founded_year = request.POST.get('founded_year', '')
        profile.founded_year = founded_year if founded_year else None
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')

        if request.FILES.get('logo'):
            profile.logo = request.FILES['logo']

        profile.save()
        messages.success(request, 'Company profile updated.')
        return redirect('company_profile')

    return render(request, 'core/company_profile.html', {'profile': profile})


def job_seeker_options(request):
    return render(request, 'core/job_seeker_options.html')


def job_seeker_login(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    if request.method == 'POST':
        form = JobSeekerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        # Clear unread messages on login page render
        storage = get_messages(request)
        for _ in storage:
            pass

        form = JobSeekerLoginForm()

    return render(request, 'core/job_seeker_login.html', {'form': form, 'next': next_url})


@login_required(login_url='employer_login')
def post_job(request):
    if settings.SUBSCRIPTION_ENABLED:
        subscription = getattr(request.user, 'subscription', None)

        if not subscription or not subscription.can_post_job():
            storage = get_messages(request)
            for _ in storage:
                pass

            messages.warning(request, "You've reached your job posting limit for this plan. Upgrade to post more jobs.")
            return redirect('subscription_plans')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobPostForm()

    return render(request, 'core/post_job.html', {'form': form})


def job_detail(request, job_id):
    job = Job.objects.get(id=job_id)
    is_owner = request.user.is_authenticated and request.user == job.posted_by
    base_template = 'core/dashboard_base.html' if is_owner else 'core/base.html'
    return render(request, 'core/job_detail.html', {
        'job': job,
        'is_owner': is_owner,
        'base_template': base_template,
    })


@login_required(login_url='employer_login')
def jobs_list(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_at')
    return render(request, 'core/jobs_list.html', {'jobs': jobs})


@login_required(login_url='job_seeker_login')
def apply_job(request, job_id):
    job = Job.objects.get(id=job_id)

    if not hasattr(request.user, 'jobseeker_profile'):
        messages.info(request, 'Please complete your profile before applying.')
        return redirect(f"{reverse('create_profile')}?next={reverse('apply_job', args=[job_id])}")

    profile = request.user.jobseeker_profile

    if request.method == 'POST':
        JobApplication.objects.create(
            job=job,
            job_seeker_profile=profile,
        )
        return redirect('application_success', job_id=job.id)

    return render(request, 'core/apply_job.html', {'job': job, 'profile': profile})


def application_success(request, job_id):
    job = Job.objects.get(id=job_id)
    return render(request, 'core/application_success.html', {'job': job})


# ---- Candidate list helper ----

def _candidate_list_context(request, applications, page_title, show_search=False, search_values=None):
    subscription = getattr(request.user, 'subscription', None)
    unlocked_ids = set(
        ResumeUnlock.objects.filter(employer=request.user, application__in=applications)
        .values_list('application_id', flat=True)
    )
    context = {
        'applications': applications,
        'page_title': page_title,
        'unlocked_ids': unlocked_ids,
        'subscription': subscription,
        'show_search': show_search,
    }
    if search_values is not None:
        context['search_values'] = search_values
    return context


@login_required(login_url='employer_login')
def new_applicants(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user, status='applied').order_by('-applied_at')
    context = _candidate_list_context(request, applications, 'New Applicants')
    return render(request, 'core/candidates_list.html', context)


@login_required(login_url='employer_login')
def manage_candidates(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user).order_by('-applied_at')
    context = _candidate_list_context(request, applications, 'Manage Candidates')
    return render(request, 'core/candidates_list.html', context)


@login_required(login_url='employer_login')
def shortlisted(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user, status='shortlisted').order_by('-applied_at')
    context = _candidate_list_context(request, applications, 'Shortlisted Candidates')
    return render(request, 'core/candidates_list.html', context)


@login_required(login_url='employer_login')
def search_resume(request):
    name = request.GET.get('name', '')
    skills = request.GET.get('skills', '')
    experience = request.GET.get('experience', '')
    education = request.GET.get('education', '')
    location = request.GET.get('location', '')

    applications = JobApplication.objects.filter(job__posted_by=request.user)

    if name:
        applications = applications.filter(
            Q(full_name__icontains=name) | Q(job_seeker_profile__full_name__icontains=name)
        )
    if skills:
        applications = applications.filter(
            Q(skills__icontains=skills) | Q(job_seeker_profile__skills__icontains=skills)
        )
    if experience:
        applications = applications.filter(
            Q(experience__icontains=experience) | Q(job_seeker_profile__experience__icontains=experience)
        )
    if education:
        applications = applications.filter(
            Q(education__icontains=education) | Q(job_seeker_profile__education__icontains=education)
        )
    if location:
        applications = applications.filter(
            Q(job__location__icontains=location) | Q(job_seeker_profile__location__icontains=location)
        )

    applications = applications.order_by('-applied_at')

    context = _candidate_list_context(
        request, applications, 'Search Resume',
        show_search=True,
        search_values={
            'name': name, 'skills': skills, 'experience': experience,
            'education': education, 'location': location,
        },
    )
    return render(request, 'core/candidates_list.html', context)


@login_required(login_url='employer_login')
@require_POST
def unlock_resume(request, application_id):
    application = JobApplication.objects.get(id=application_id)

    if application.job.posted_by != request.user:
        messages.error(request, 'You are not authorized to do that.')
        return redirect('manage_candidates')

    already_unlocked = ResumeUnlock.objects.filter(employer=request.user, application=application).exists()
    if already_unlocked:
        return redirect(request.META.get('HTTP_REFERER', 'manage_candidates'))

    if settings.SUBSCRIPTION_ENABLED:
        subscription = getattr(request.user, 'subscription', None)
        if not subscription or not subscription.can_view_resume():
            messages.warning(request, "You've hit your resume view limit. Upgrade your plan to view more candidates.")
            return redirect('subscription_plans')

    ResumeUnlock.objects.create(employer=request.user, application=application)

    if settings.SUBSCRIPTION_ENABLED:
        subscription.resumes_viewed_count += 1
        subscription.save()

    return redirect(request.META.get('HTTP_REFERER', 'manage_candidates'))


@login_required(login_url='employer_login')
def update_application_status(request, application_id):
    application = JobApplication.objects.get(id=application_id)

    if application.job.posted_by != request.user:
        messages.error(request, 'You are not authorized to do that.')
        return redirect('manage_candidates')

    new_status = request.POST.get('status')
    if new_status in dict(JobApplication.STATUS_CHOICES):
        application.status = new_status
        application.save()

    return redirect(request.META.get('HTTP_REFERER', 'manage_candidates'))


def inquiries(request):
    inquiries = Inquiry.objects.all().order_by('-created_at')
    return render(request, 'core/inquiries.html', {'inquiries': inquiries})


@login_required(login_url='employer_login')
def add_candidate(request):
    if request.method == 'POST':
        form = EmployerAddCandidateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate added successfully.')
            return redirect('manage_candidates')
    else:
        form = EmployerAddCandidateForm(user=request.user)
    return render(request, 'core/add_candidate.html', {'form': form})


@login_required(login_url='employer_login')
def add_interview(request):
    if request.method == 'POST':
        form = InterviewForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('employer_dashboard')
    else:
        form = InterviewForm(user=request.user)
    return render(request, 'core/add_interview.html', {'form': form})


@login_required(login_url='job_seeker_login')
def create_profile(request):
    if hasattr(request.user, 'jobseeker_profile'):
        return redirect('edit_profile')

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully.')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = JobSeekerProfileForm()

    return render(request, 'core/create_profile.html', {'form': form})


@login_required(login_url='job_seeker_login')
def edit_profile(request):
    profile, created = JobSeekerProfile.objects.get_or_create(
        user=request.user, defaults={'full_name': request.user.username, 'phone': ''}
    )

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('edit_profile')
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {'form': form})


# ---- Subscription plans / Razorpay payment ----

@login_required(login_url='employer_login')
def subscription_plans(request):
    plans = SubscriptionPlan.objects.all().order_by('price')
    current_sub = getattr(request.user, 'subscription', None)
    jobs_posted_live = Job.objects.filter(posted_by=request.user).count()
    return render(request, 'core/subscription_plans.html', {
        'plans': plans,
        'current_sub': current_sub,
        'jobs_posted_live': jobs_posted_live,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required(login_url='employer_login')
@require_POST
def create_razorpay_order(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)

    if plan.price == 0:
        EmployerSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'expires_at': timezone.now() + timedelta(days=plan.duration_days),
                'jobs_posted_count': 0,
                'resumes_viewed_count': 0,
            }
        )
        return JsonResponse({'free': True, 'redirect': reverse('employer_dashboard')})

    amount_paise = plan.price * 100
    order = razorpay_client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {'plan_id': plan.id, 'user_id': request.user.id},
    })

    return JsonResponse({
        'free': False,
        'order_id': order['id'],
        'amount': amount_paise,
        'key_id': settings.RAZORPAY_KEY_ID,
        'plan_name': plan.name,
        'user_email': request.user.email,
    })


@csrf_exempt
@login_required(login_url='employer_login')
@require_POST
def verify_payment(request):
    data = json.loads(request.body)
    plan_id = data.get('plan_id')

    params_dict = {
        'razorpay_order_id': data.get('razorpay_order_id'),
        'razorpay_payment_id': data.get('razorpay_payment_id'),
        'razorpay_signature': data.get('razorpay_signature'),
    }

    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'error': 'Signature verification failed'}, status=400)

    plan = SubscriptionPlan.objects.get(id=plan_id)
    EmployerSubscription.objects.update_or_create(
        user=request.user,
        defaults={
            'plan': plan,
            'expires_at': timezone.now() + timedelta(days=plan.duration_days),
            'jobs_posted_count': 0,
            'resumes_viewed_count': 0,
        }
    )

    return JsonResponse({'success': True, 'redirect': reverse('employer_dashboard')})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='employer_login')
@require_POST
def delete_job(request, job_id):
    job = Job.objects.get(id=job_id)

    if job.posted_by != request.user:
        messages.error(request, 'You are not authorized to do that.')
        return redirect('jobs_list')

    job.delete()
    messages.success(request, 'Job posting removed.')
    return redirect('jobs_list')

@login_required(login_url='employer_login')
def candidate_detail(request, application_id):
    application = JobApplication.objects.get(id=application_id)

    if application.job.posted_by != request.user:
        messages.error(request, 'You are not authorized to view that.')
        return redirect('employer_dashboard')

    return render(request, 'core/candidate_detail.html', {'application': application})

def internships(request):
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    jobs = Job.objects.filter(job_type='internship').order_by('-posted_at')

    if query:
        jobs = jobs.filter(Q(job_title__icontains=query) | Q(skills_required__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)

    return render(request, 'core/internships.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
    })