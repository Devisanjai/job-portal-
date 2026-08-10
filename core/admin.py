from django.contrib import admin
from .models import (
    Profile, Job, JobApplication, JobSeekerProfile, Inquiry, Interview,
    SubscriptionPlan, EmployerSubscription, ResumeUnlock, Notification,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_employer', 'company_name', 'phone', 'is_email_verified', 'created_at')
    list_filter = ('is_employer', 'is_email_verified')
    search_fields = ('user__username', 'company_name')


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'location', 'preferred_job_type', 'is_email_verified', 'created_at')
    list_filter = ('preferred_job_type', 'is_email_verified')
    search_fields = ('full_name', 'user__username', 'skills', 'location')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'posted_by', 'location', 'job_type', 'experience_required', 'number_of_openings', 'posted_at')
    list_filter = ('job_type', 'experience_required')
    search_fields = ('job_title', 'location', 'skills_required', 'company_name')
    date_hierarchy = 'posted_at'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('display_full_name', 'job', 'status', 'display_email', 'display_phone', 'applied_at')
    list_filter = ('status', 'job')
    search_fields = ('full_name', 'email', 'skills', 'job_seeker_profile__full_name')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'status', 'email', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_at', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('application__full_name',)
    date_hierarchy = 'scheduled_at'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'job_post_limit', 'resume_view_limit')


@admin.register(EmployerSubscription)
class EmployerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'expires_at', 'jobs_posted_count', 'resumes_viewed_count')
    list_filter = ('plan',)
    search_fields = ('user__username',)


@admin.register(ResumeUnlock)
class ResumeUnlockAdmin(admin.ModelAdmin):
    list_display = ('employer', 'application', 'unlocked_at')
    search_fields = ('employer__username',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'