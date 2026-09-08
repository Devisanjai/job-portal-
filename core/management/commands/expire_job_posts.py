from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Job


class Command(BaseCommand):
    help = (
        "Hide job posts whose expiry date has passed. "
        "Run this on a schedule (cron / Task Scheduler) to auto-expire old posts."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which posts would be expired without changing anything.',
        )

    def handle(self, *args, **options):
        from django.urls import reverse
        from core.views import create_notification

        dry_run = options['dry_run']
        expired = Job.objects.filter(is_active=True, expires_at__lte=timezone.now())
        count = 0

        for job in expired:
            count += 1
            if dry_run:
                self.stdout.write(f"[dry-run] {job.job_title} (id={job.id}, expired {job.expires_at:%d %b %Y})")
                continue

            job.is_active = False
            job.inactive_reason = 'expired'
            job.save(update_fields=['is_active', 'inactive_reason'])

            create_notification(
                user=job.posted_by,
                message=(
                    f"Your job posting \"{job.job_title}\" reached its expiry date and has been "
                    f"hidden from job seekers. You can reactivate it from My Posted Jobs."
                ),
                notification_type='general',
                link=reverse('jobs_list'),
            )
            self.stdout.write(f"Expired: {job.job_title} (id={job.id})")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"{count} job post(s) would be expired."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Expired {count} job post(s)."))
