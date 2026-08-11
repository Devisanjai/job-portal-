from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Job, JobApplication, JobSeekerProfile, Profile


class JobSeekerSignupLoginTests(TestCase):
    def test_new_username_creates_account_and_logs_in(self):
        response = self.client.post(reverse('job_seeker_login'), {
            'username': 'newseeker@test.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(User.objects.filter(username='newseeker@test.com').count(), 1)
        user = User.objects.get(username='newseeker@test.com')
        self.assertTrue(JobSeekerProfile.objects.filter(user=user).exists())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('create_profile'))
        
    def test_existing_username_wrong_password_shows_error(self):
        user = User.objects.create_user(username='existing1', password='CorrectPass123!')
        JobSeekerProfile.objects.create(user=user, full_name='Existing', phone='123')

        response = self.client.post(reverse('job_seeker_login'), {
            'username': 'existing1',
            'password': 'WrongPassword!',
        }, follow=True)
        self.assertContains(response, 'Incorrect password')

    def test_existing_username_correct_password_logs_in(self):
        user = User.objects.create_user(username='existing2', password='CorrectPass123!')
        JobSeekerProfile.objects.create(user=user, full_name='Existing2', phone='123')

        response = self.client.post(reverse('job_seeker_login'), {
            'username': 'existing2',
            'password': 'CorrectPass123!',
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class EmployerLoginTests(TestCase):
    def test_new_email_creates_employer_account(self):
        response = self.client.post(reverse('employer_login'), {
            'email': 'newcompany@test.com',
            'password': 'TestPass123!',
            'company_name': 'Test Co',
        })
        self.assertTrue(User.objects.filter(username='newcompany@test.com').exists())
        user = User.objects.get(username='newcompany@test.com')
        self.assertTrue(Profile.objects.filter(user=user, is_employer=True).exists())
        self.assertRedirects(response, reverse('employer_dashboard'))


class ApplyJobTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(username='employer1', password='pass123')
        Profile.objects.create(user=self.employer, is_employer=True, company_name='Acme')

        self.job = Job.objects.create(
            posted_by=self.employer,
            job_title='Backend Developer',
            job_description='Build things',
            experience_required='fresher',
            job_type='full-time',
            location='Remote',
        )

        self.seeker = User.objects.create_user(username='seeker@test.com', password='pass123')
        self.profile = JobSeekerProfile.objects.create(
            user=self.seeker, full_name='Test Seeker', phone='9999999999'
        )

    def test_apply_creates_application(self):
        self.client.login(username='seeker@test.com', password='pass123')
        response = self.client.post(reverse('apply_job', args=[self.job.id]))
        self.assertTrue(
            JobApplication.objects.filter(job=self.job, job_seeker_profile=self.profile).exists()
        )
        self.assertRedirects(response, reverse('application_success', args=[self.job.id]))

    def test_duplicate_application_blocked(self):
        self.client.login(username='seeker@test.com', password='pass123')
        self.client.post(reverse('apply_job', args=[self.job.id]))
        self.client.post(reverse('apply_job', args=[self.job.id]))
        self.assertEqual(
            JobApplication.objects.filter(job=self.job, job_seeker_profile=self.profile).count(), 1
        )

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('job-seeker-login', response.url)


class ApplicationStatusChangeTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(username='employer2', password='pass123')
        Profile.objects.create(user=self.employer, is_employer=True, company_name='Acme2')

        self.other_employer = User.objects.create_user(username='employer3', password='pass123')
        Profile.objects.create(user=self.other_employer, is_employer=True, company_name='OtherCo')

        self.job = Job.objects.create(
            posted_by=self.employer,
            job_title='Designer',
            job_description='Design things',
            experience_required='fresher',
            job_type='full-time',
            location='Remote',
        )

        self.seeker = User.objects.create_user(username='seeker2@test.com', password='pass123')
        self.profile = JobSeekerProfile.objects.create(
            user=self.seeker, full_name='Seeker Two', phone='8888888888'
        )
        self.application = JobApplication.objects.create(job=self.job, job_seeker_profile=self.profile)

    def test_owner_can_change_status(self):
        self.client.login(username='employer2', password='pass123')
        self.client.post(reverse('update_application_status', args=[self.application.id]), {
            'status': 'shortlisted',
        })
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'shortlisted')

    def test_non_owner_cannot_change_status(self):
        self.client.login(username='employer3', password='pass123')
        self.client.post(reverse('update_application_status', args=[self.application.id]), {
            'status': 'shortlisted',
        })
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')