from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import SignUpForm, EmployerLoginForm, JobSeekerLoginForm


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