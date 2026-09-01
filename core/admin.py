from django.contrib import admin
from .models import AdminLoginOTP
from .models import (
    Profile, Job, JobApplication, JobSeekerProfile, Inquiry, Interview,
    SubscriptionPlan, EmployerSubscription, ResumeUnlock, Notification,
    SavedJob, JobSeekerSignupOTP,VerificationDocument, BackgroundVerification
)

#profilleAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_employer', 'company_name', 'phone', 'is_email_verified', 'created_at')
    list_filter = ('is_employer', 'is_email_verified')
    search_fields = ('user__username', 'company_name')

#JobSeekerProfileAdmin ----------------------------------------------------------------------------------------------------------
@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'location', 'preferred_job_type', 'is_email_verified', 'created_at')
    list_filter = ('preferred_job_type', 'is_email_verified')
    search_fields = ('full_name', 'user__username', 'skills', 'location')

#jobAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'posted_by', 'location', 'job_type', 'experience_required', 'number_of_openings', 'posted_at')
    list_filter = ('job_type', 'experience_required')
    search_fields = ('job_title', 'location', 'skills_required', 'company_name')
    date_hierarchy = 'posted_at'

#jobApplicationAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('display_full_name', 'job', 'status', 'display_email', 'display_phone', 'applied_at')
    list_filter = ('status', 'job')
    search_fields = ('full_name', 'email', 'skills', 'job_seeker_profile__full_name')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'

#InquiryAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'status', 'email', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject')

#InterviewAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_at', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('application__full_name',)
    date_hierarchy = 'scheduled_at'

#SubscriptionPlanAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'job_post_limit', 'resume_view_limit')

#EmployerSubscriptionAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(EmployerSubscription)
class EmployerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'expires_at', 'jobs_posted_count', 'resumes_viewed_count')
    list_filter = ('plan',)
    search_fields = ('user__username',)

#ResumeUnlockAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(ResumeUnlock)
class ResumeUnlockAdmin(admin.ModelAdmin):
    list_display = ('employer', 'application', 'unlocked_at')
    search_fields = ('employer__username',)

#NotificationAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'
#SavedJobAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    search_fields = ('user__username', 'job__job_title')
    date_hierarchy = 'saved_at'

#JobSeekerSignupOTPAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(JobSeekerSignupOTP)
class JobSeekerSignupOTPAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'attempts', 'created_at', 'expires_at')
    search_fields = ('username', 'email')
    readonly_fields = ('otp_code', 'password_hash')

#AdminLoginOTPAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(AdminLoginOTP)
class AdminLoginOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'attempts', 'created_at', 'expires_at')
    readonly_fields = ('otp_code',)
#verificationDocumentAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('job_seeker_profile', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('job_seeker_profile__full_name',)

#backgroundVerificationAdmin ---------------------------------------------------------------------------------------------------------------
@admin.register(BackgroundVerification)
class BackgroundVerificationAdmin(admin.ModelAdmin):
    list_display = ('job_seeker_profile', 'status', 'has_new_documents', 'verified_by', 'verified_at')
    list_filter = ('status', 'has_new_documents')
    search_fields = ('job_seeker_profile__full_name',)
    readonly_fields = ('created_at', 'updated_at')