from django.core.management.base import BaseCommand
from core.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Seed default subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {'name': 'Free', 'price': 0, 'duration_days': 30, 'job_post_limit': 2, 'resume_view_limit': 5},
            {'name': 'Basic', 'price': 499, 'duration_days': 30, 'job_post_limit': 10, 'resume_view_limit': 50},
            {'name': 'Premium', 'price': 1499, 'duration_days': 30, 'job_post_limit': 50, 'resume_view_limit': 500},
        ]
        for p in plans:
            obj, created = SubscriptionPlan.objects.update_or_create(
                name=p['name'], defaults=p
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"{status}: {obj.name}"))