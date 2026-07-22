from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, EmployerLoginForm, JobSeekerLoginForm, JobPostForm
from .models import Job
from .forms import SignUpForm, EmployerLoginForm, JobSeekerLoginForm, JobPostForm, JobApplicationForm
from .models import Job, JobApplication

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
    return render(request, 'core/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

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

            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'No account found with that email.')
                return render(request, 'core/employer_login.html', {'form': form})

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('employer_dashboard')
            else:
                messages.error(request, 'Incorrect password.')
    else:
        form = EmployerLoginForm()

    return render(request, 'core/employer_login.html', {'form': form})


@login_required(login_url='employer_login')
def employer_dashboard(request):
    context = {
        'current_openings': 7,
        'candidates_total': 907,
        'candidates_pending': 966,
        'interview_list': 0,
        'inquiries_total': 93,
        'inquiries_unread': 93,
        'upcoming_interviews': [
            {'name': 'Vijay Kumar', 'status': 'Hire', 'role': 'Urgent Requirement PHP Developer - Noida (3-6 yrs)', 'date': '11/01/2026 - 13:40 PM'},
            {'name': 'Ramesh Kumar', 'status': 'Offer', 'role': 'Suitable Position For PHP Developer at Rajkot (1-2 yrs)', 'date': '11/01/2026 - 13:40 PM'},
        ],
        'recent_activity': [
            {'name': 'Brijesh Kumar', 'status': 'Hire', 'note': 'Communication skills are good and have database and JavaScript knowledge. Preferred location is Delhi.', 'time': '1 month ago'},
            {'name': 'Rajesh Kumar', 'status': 'Offer', 'note': 'Provide offer for candidate.', 'time': '1 month ago'},
        ],
    }
    return render(request, 'core/employer_dashboard.html', context)


def job_seeker_options(request):
    return render(request, 'core/job_seeker_options.html')


def job_seeker_login(request):
    if request.method == 'POST':
        form = JobSeekerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = JobSeekerLoginForm()

    return render(request, 'core/job_seeker_login.html', {'form': form})


@login_required(login_url='employer_login')
def post_job(request):
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


@login_required(login_url='employer_login')
def job_detail(request, job_id):
    job = Job.objects.get(id=job_id)
    return render(request, 'core/job_detail.html', {'job': job})

@login_required(login_url='employer_login')
def jobs_list(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_at')
    return render(request, 'core/jobs_list.html', {'jobs': jobs})



def apply_job(request, job_id):
    job = Job.objects.get(id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            return redirect('application_success')
    else:
        form = JobApplicationForm()

    return render(request, 'core/apply_job.html', {'form': form, 'job': job})


def application_success(request):
    return render(request, 'core/application_success.html')


@login_required(login_url='employer_login')
def new_applicants(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user, status='applied').order_by('-applied_at')
    return render(request, 'core/candidates_list.html', {'applications': applications, 'page_title': 'New Applicants'})


@login_required(login_url='employer_login')
def manage_candidates(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user).order_by('-applied_at')
    return render(request, 'core/candidates_list.html', {'applications': applications, 'page_title': 'Manage Candidates'})


@login_required(login_url='employer_login')
def search_resume(request):
    query = request.GET.get('q', '')
    applications = JobApplication.objects.filter(job__posted_by=request.user)
    if query:
        applications = applications.filter(skills__icontains=query)
    return render(request, 'core/candidates_list.html', {'applications': applications, 'page_title': 'Search Resume', 'search_query': query, 'show_search': True})


@login_required(login_url='employer_login')
def shortlisted(request):
    applications = JobApplication.objects.filter(job__posted_by=request.user, status='shortlisted').order_by('-applied_at')
    return render(request, 'core/candidates_list.html', {'applications': applications, 'page_title': 'Shortlisted Candidates'})

@login_required(login_url='employer_login')
def update_application_status(request, application_id):
    application = JobApplication.objects.get(id=application_id)

    # security check: make sure this employer owns the job this application is for
    if application.job.posted_by != request.user:
        messages.error(request, 'You are not authorized to do that.')
        return redirect('manage_candidates')

    new_status = request.POST.get('status')
    if new_status in dict(JobApplication.STATUS_CHOICES):
        application.status = new_status
        application.save()

    return redirect(request.META.get('HTTP_REFERER', 'manage_candidates'))