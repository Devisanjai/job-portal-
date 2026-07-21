from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import SignUpForm, EmployerLoginForm, JobSeekerLoginForm

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
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')
    else:
        form = EmployerLoginForm()

    return render(request, 'core/employer_login.html', {'form': form})
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