from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.db.models.signals import post_save
from django.dispatch import receiver
from .storage import protected_storage

def validate_file_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size must be under {max_size_mb}MB.')

# Profile model for both employers and job seekers -----------------------------------------------------------------------
class Profile(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    is_employer = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    about = models.TextField(blank=True, help_text="Brief description of the company")
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

#Job model ---------------------------------------------------------------------------------------------------------------
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
        ('Walk-in', 'Walk-in'),
    ]

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True, default='')
    job_description = models.TextField()
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    number_of_openings = models.PositiveIntegerField(default=1)
    salary_range = models.CharField(max_length=100, blank=True)
    skills_required = models.CharField(max_length=300, blank=True, help_text="Comma-separated skills")
    posted_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)
    APPROVAL_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    
    def __str__(self):
        return self.job_title


#JobApplication model ---------------------------------------------------------------------------------------------------------------
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'New Applicant'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')

    # Linked path — set when a logged-in job seeker with a profile applies
    job_seeker_profile = models.ForeignKey(
        'JobSeekerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications'
    )

    # Walk-in path — used only when job_seeker_profile is null (employer manually added this candidate)
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    education = models.CharField(max_length=200, blank=True)
    skills = models.CharField(max_length=300, blank=True, help_text="Comma-separated skills")
    experience = models.CharField(max_length=100, blank=True)
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf']), validate_file_size],
        help_text="PDF only, max 5MB"
    )

    cover_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    is_bookmarked = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.display_full_name} - {self.job.job_title}"

    # --- Helpers so templates always show current data, whichever path was used ---
    @property
    def display_full_name(self):
        return self.job_seeker_profile.full_name if self.job_seeker_profile else self.full_name

    @property
    def display_email(self):
        return self.job_seeker_profile.user.email if self.job_seeker_profile else self.email

    @property
    def display_phone(self):
        return self.job_seeker_profile.phone if self.job_seeker_profile else self.phone

    @property
    def display_education(self):
        return self.job_seeker_profile.education if self.job_seeker_profile else self.education

    @property
    def display_skills(self):
        return self.job_seeker_profile.skills if self.job_seeker_profile else self.skills

    @property
    def display_experience(self):
        return self.job_seeker_profile.experience if self.job_seeker_profile else self.experience

    @property
    def display_resume(self):
        return self.job_seeker_profile.resume if self.job_seeker_profile else self.resume

#Inquiry model ---------------------------------------------------------------------------------------------------------------
class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
        ('Replied', 'Replied'),
        ('Closed', 'Closed'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

#Interview model ---------------------------------------------------------------------------------------------------------------
class Interview(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('hire', 'Hire'),
        ('offer', 'Offer'),
        ('reject', 'Reject'),
        ('completed', 'Completed'),
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.application.full_name} - {self.scheduled_at.strftime('%d/%m/%Y')}"

#JobSeekerProfile model ---------------------------------------------------------------------------------------------------------------
class JobSeekerProfile(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=150, blank=True)
    education = models.CharField(max_length=200, blank=True)
    certificates = models.TextField(blank=True, help_text="List certificates, one per line or comma-separated")
    skills = models.CharField(max_length=300, blank=True, help_text="Comma-separated skills")
    experience = models.CharField(max_length=100, blank=True)
    preferred_job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True)
    is_experienced = models.BooleanField(default=False, help_text="False = Fresher, True = Experienced")
    resume = models.FileField(
        upload_to='profile_resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf']), validate_file_size],
        help_text="PDF only, max 5MB"
    )
    ats_score = models.PositiveIntegerField(null=True, blank=True, help_text="Placeholder for now")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

#VerificationDocument model ---------------------------------------------------------------------------------------------------------------
class VerificationDocument(models.Model):
    DOCUMENT_TYPES = [
        ('10th_marksheet', '10th Marksheet'),
        ('12th_marksheet', '12th Marksheet'),
        ('degree_marksheet', 'Degree/College Marksheet'),
        ('relieving_letter', 'Relieving Letter'),
        ('payslip', 'Payslip'),
        ('offer_letter', 'Previous Offer Letter'),
        ('other', 'Other'),
    ]
    job_seeker_profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='verification_documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(
        upload_to='verification_docs/',
        storage=protected_storage,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']), validate_file_size],
        help_text="PDF or image, max 5MB"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_seeker_profile.full_name} - {self.get_document_type_display()}"


#BackgroundVerification model ---------------------------------------------------------------------------------------------------------------
class BackgroundVerification(models.Model):
    STATUS_CHOICES = [
        ('not_requested', 'Not Requested'),
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged'),
    ]
    job_seeker_profile = models.OneToOneField(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='background_verification'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_requested')
    has_new_documents = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True, help_text="Visible to admin/verification team only")
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications_done'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_seeker_profile.full_name} - {self.get_status_display()}"


#SubscriptionPlan model ---------------------------------------------------------------------------------------------------------------
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField(help_text="Price in INR")
    duration_days = models.PositiveIntegerField(default=30)
    job_post_limit = models.PositiveIntegerField()
    resume_view_limit = models.PositiveIntegerField(default=0)
    includes_bgv_access = models.BooleanField(default=False, help_text="Whether this plan lets employers view background verification status")

    def __str__(self):
        return self.name

#EmployerSubscription model ---------------------------------------------------------------------------------------------------------------
class EmployerSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    jobs_posted_count = models.PositiveIntegerField(default=0)
    resumes_viewed_count = models.PositiveIntegerField(default=0)

    def is_active(self):
        from django.utils import timezone
        return timezone.now() < self.expires_at

    def can_post_job(self):
        actual_count = Job.objects.filter(posted_by=self.user).count()
        return self.is_active() and actual_count < self.plan.job_post_limit

    def can_view_resume(self):
        return self.is_active() and self.resumes_viewed_count < self.plan.resume_view_limit

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"


#ResumeUnlock model ---------------------------------------------------------------------------------------------------------------
class ResumeUnlock(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_unlocks')
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='unlocked_by')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'application')

    def __str__(self):
        return f"{self.employer.username} unlocked {self.application_id}"


#Notification model ---------------------------------------------------------------------------------------------------------------
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application_status', 'Application Status Update'),
        ('new_applicant', 'New Applicant'),
        ('profile_reminder', 'Profile Reminder'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, help_text="URL path to redirect to, e.g. /my-applications/")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:40]}"


#SavedJob model ---------------------------------------------------------------------------------------------------------------
class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.job.job_title}"

    

#JobSeekerSignupOTP model ---------------------------------------------------------------------------------------------------------------
class JobSeekerSignupOTP(models.Model):
    """
    Holds a job seeker signup in a 'pending' state until the email OTP is
    verified. No User/JobSeekerProfile is created until then.
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128, help_text="Already-hashed password, never stored in plain text")
    otp_code = models.CharField(max_length=6)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Pending signup: {self.username} ({self.email})"

#AdminLoginOTP model ---------------------------------------------------------------------------------------------------------------
class AdminLoginOTP(models.Model):
    """
    Second-factor OTP for the superuser admin login. Created after password
    verification succeeds; login() only happens after the code is confirmed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Admin OTP for {self.user.username}"

@receiver(post_save, sender=JobSeekerProfile)
def create_background_verification(sender, instance, created, **kwargs):
    if created:
        BackgroundVerification.objects.get_or_create(job_seeker_profile=instance)

class VerifierProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verifier_profile')
    is_active_verifier = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifiers_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verifier: {self.user.username}"