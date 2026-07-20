from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('employer-login/', views.employer_login, name='employer_login'),
    path('job-seekers/', views.job_seeker_options, name='job_seeker_options'),
    path('job-seeker-login/', views.job_seeker_login, name='job_seeker_login'),
]