from django import forms
from django.contrib.auth.models import User
from .models import Job, JobApplication, Interview, JobSeekerProfile
#SignUpForm -------------------------------------------------------------------------------------------------
class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400'
            }),
        }

#EmployerLoginForm -------------------------------------------------------------------------------------------------
class EmployerLoginForm(forms.Form):
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Company Name',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Company Email',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )


#JobSeekerLoginForm -------------------------------------------------------------------------------------------------
class JobSeekerLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Password'
        })
    )


#JobSeekerProfileForm -------------------------------------------------------------------------------------------------
class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['full_name', 'phone', 'location', 'education', 'certificates', 'skills', 'experience', 'preferred_job_type', 'resume', 'is_experienced']
        widgets = {
            'is_experienced': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }
        labels = {
            'is_experienced': 'I have professional work experience (leave unchecked if you are a fresher)',
        }
        fields = ['full_name', 'phone', 'location', 'education', 'certificates', 'skills', 'experience', 'preferred_job_type', 'resume']


#JobSeekerProfileEditForm -------------------------------------------------------------------------------------------------
class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'company_name', 'job_description', 'experience_required', 'job_type', 'location', 'number_of_openings', 'salary_range', 'skills_required']
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. Frontend Developer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. Deploynix Tech Pvt Ltd'
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'Describe the role, responsibilities, and requirements',
                'rows': 5
            }),
            'experience_required': forms.Select(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400'
            }),
            'job_type': forms.Select(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. Coimbatore, Tamil Nadu'
            }),
            'number_of_openings': forms.NumberInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'min': 1
            }),
            'salary_range': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. ₹3,00,000 - ₹5,00,000 per year'
            }),
            'skills_required': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. Python, Django, React'
            }),
        }


#JobApplicationForm -------------------------------------------------------------------------------------------------
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'education', 'skills', 'experience', 'resume', 'cover_note']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': '10-digit phone number'
            }),
            'education': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. BSc Information Technology'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. Python, Django, MySQL'
            }),
            'experience': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'e.g. 1 year / Fresher'
            }),
            'resume': forms.ClearableFileInput(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm'
            }),
            'cover_note': forms.Textarea(attrs={
                'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
                'placeholder': 'Tell the employer why you\'re a good fit (optional)',
                'rows': 4
            }),
        }

#EmployerAddCandidateForm -------------------------------------------------------------------------------------------------
class EmployerAddCandidateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job', 'full_name', 'email', 'phone', 'education', 'skills', 'experience', 'resume', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['job'].queryset = Job.objects.filter(posted_by=user)


#InterviewForm -------------------------------------------------------------------------------------------------
class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['application', 'scheduled_at', 'status', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['application'].queryset = JobApplication.objects.filter(job__posted_by=user)


#jobSeekerLoginForm -------------------------------------------------------------------------------------------------
class JobSeekerLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Email (only needed the first time)'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Password'
        })
    )


#OTPVerifyForm -------------------------------------------------------------------------------------------------
class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-3 text-center text-2xl tracking-[0.5em] font-semibold focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'maxlength': '6',
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data['otp_code'].strip()
        if not code.isdigit():
            raise forms.ValidationError('Enter the 6-digit code exactly as sent to your email.')
        return code