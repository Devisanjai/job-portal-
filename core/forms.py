from django import forms
from django.contrib.auth.models import User

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


class EmployerLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Company Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-2 border-gray-400 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400',
            'placeholder': 'Password'
        })
    )
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