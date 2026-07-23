from django.contrib import admin
from .models import Profile, Job, JobApplication

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_employer', 'company_name', 'phone', 'created_at')
    list_filter = ('is_employer',)
    search_fields = ('user__username', 'company_name')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'posted_by', 'location', 'job_type', 'experience_required', 'posted_at')
    list_filter = ('job_type', 'experience_required')
    search_fields = ('job_title', 'location', 'skills_required')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'status', 'email', 'phone', 'applied_at')
    list_filter = ('status', 'job')
    search_fields = ('full_name', 'email', 'skills')
    list_editable = ('status',)