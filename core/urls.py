from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('employer-login/', views.employer_login, name='employer_login'),
    path('employer-dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('job-seekers/', views.job_seeker_options, name='job_seeker_options'),
    path('job-seeker-login/', views.job_seeker_login, name='job_seeker_login'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('post-job/', views.post_job, name='post_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/', views.jobs_list, name='jobs_list'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('application-success/', views.application_success, name='application_success'),
    path('candidates/new/', views.new_applicants, name='new_applicants'),
    path('candidates/manage/', views.manage_candidates, name='manage_candidates'),
    path('candidates/search/', views.search_resume, name='search_resume'),
    path('candidates/shortlisted/', views.shortlisted, name='shortlisted'),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
]