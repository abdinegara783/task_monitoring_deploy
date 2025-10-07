from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:
    BackgroundScheduler = None

from dashboard.models import ShiftSchedule, User


def apply_today_shifts():
    today = timezone.localdate()
    updated = 0
    schedules = ShiftSchedule.objects.filter(date=today, is_active=True)
    for sched in schedules.select_related("foreman"):
        if sched.foreman.shift != sched.shift:
            sched.foreman.shift = sched.shift
            sched.foreman.save(update_fields=["shift", "updated_at"])
            updated += 1
    return updated


class Command(BaseCommand):
    help = "Run APScheduler to apply daily shift schedules automatically."

    def handle(self, *args, **options):
        if BackgroundScheduler is None:
            self.stderr.write(
                self.style.ERROR(
                    "APScheduler not installed. Please add 'APScheduler' and 'django-apscheduler' to requirements and install."
                )
            )
            return

        scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))

        # Apply today's shifts immediately at start
        with transaction.atomic():
            applied = apply_today_shifts()
            self.stdout.write(self.style.SUCCESS(f"Applied {applied} shift(s) at startup."))

        # Schedule job every day at 00:01
        scheduler.add_job(apply_today_shifts, "cron", hour=0, minute=1, id="apply_daily_shifts", replace_existing=True)

        self.stdout.write(self.style.SUCCESS("Shift scheduler started. Running in background..."))

        try:
            scheduler.start()
            # Keep alive
            import time

            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.WARNING("Shift scheduler stopped."))