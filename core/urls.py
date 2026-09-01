from django.urls import path
from . import views
from . import admin_panel_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('vacancies/', views.job_vacancies, name='job_vacancies'),
    path('signup/', views.signup, name='signup'),
    path('employer-login/', views.employer_login, name='employer_login'),
    path('employer-dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('job-seekers/', views.job_seeker_options, name='job_seeker_options'),
    path('job-seeker-login/', views.job_seeker_login, name='job_seeker_login'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('post-job/', views.post_job_select, name='post_job_select'),
    path('post-job/<str:job_type>/', views.post_job, name='post_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/', views.jobs_list, name='jobs_list'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('candidates/new/', views.new_applicants, name='new_applicants'),
    path('candidates/manage/', views.manage_candidates, name='manage_candidates'),
    path('candidates/search/', views.search_resume, name='search_resume'),
    path('candidates/shortlisted/', views.shortlisted, name='shortlisted'),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('application-success/<int:job_id>/', views.application_success, name='application_success'),
    path('inquiries/', views.inquiries, name='inquiries'),
    path('candidates/add/', views.add_candidate, name='add_candidate'),
    path('interview/add/', views.add_interview, name='add_interview'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('plans/', views.subscription_plans, name='subscription_plans'),
    path('plans/<int:plan_id>/order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('plans/verify/', views.verify_payment, name='verify_payment'),
    path('candidates/<int:application_id>/unlock/', views.unlock_resume, name='unlock_resume'),
    path('logout/', views.logout_view, name='logout'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('company-profile/', views.company_profile, name='company_profile'),
    path('candidate/<int:application_id>/', views.candidate_detail, name='candidate_detail'),
    path('internships/', views.internships, name='internships'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-applications/<int:application_id>/delete/', views.delete_application, name='delete_application'),
    path('ats-checker/', views.ats_checker, name='ats_checker'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/unread-count/', views.unread_notification_count, name='unread_notification_count'),
    path('job/<int:job_id>/save/', views.toggle_save_job, name='toggle_save_job'),
    path('saved-jobs/', views.saved_jobs_list, name='saved_jobs_list'),
    path('walk-in-jobs/', views.walkin_jobs, name='walkin_jobs'),
    path('employer-reports/', views.employer_reports, name='employer_reports'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-verify-otp/', views.admin_verify_otp, name='admin_verify_otp'),
    path('employer-settings/', views.employer_settings, name='employer_settings'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('control-panel/verifications/', admin_panel_views.admin_verifications_list, name='admin_verifications_list'),
    path('control-panel/verifications/<int:verification_id>/', admin_panel_views.admin_verification_detail, name='admin_verification_detail'),
    # OTP Signup Verification
    path('verify-signup-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('resend-signup-otp/', views.resend_signup_otp, name='resend_signup_otp'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset_form.html',
        email_template_name='core/password_reset_email.html',
        subject_template_name='core/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Email Verification Links
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Custom Admin Control Panel
    path('control-panel/', admin_panel_views.admin_dashboard, name='admin_dashboard'),
    path('control-panel/jobs/', admin_panel_views.admin_jobs_list, name='admin_jobs_list'),
    path('control-panel/jobs/<int:job_id>/set-status/<str:status>/', admin_panel_views.admin_job_set_status, name='admin_job_set_status'),
    path('control-panel/jobs/<int:job_id>/delete/', admin_panel_views.admin_job_delete, name='admin_job_delete'),
    path('control-panel/users/', admin_panel_views.admin_users_list, name='admin_users_list'),
    path('control-panel/users/<int:user_id>/toggle-active/', admin_panel_views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('control-panel/inquiries/', admin_panel_views.admin_inquiries_list, name='admin_inquiries_list'),
    path('control-panel/inquiries/<int:inquiry_id>/update-status/', admin_panel_views.admin_inquiry_update_status, name='admin_inquiry_update_status'),
]