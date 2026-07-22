from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    is_employer = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Job(models.Model):
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('0-1', '0-1 years'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5+', '5+ years'),
    ]

    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    number_of_openings = models.PositiveIntegerField(default=1)
    salary_range = models.CharField(max_length=100, blank=True)
    skills_required = models.CharField(max_length=300, blank=True, help_text="Comma-separated skills")
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    education = models.CharField(max_length=200)
    skills = models.CharField(max_length=300, help_text="Comma-separated skills")
    experience = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    cover_note = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.job_title}"

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'New Applicant'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    education = models.CharField(max_length=200)
    skills = models.CharField(max_length=300, help_text="Comma-separated skills")
    experience = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    cover_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.job_title}"
