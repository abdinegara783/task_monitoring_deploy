from django.core.management.base import BaseCommand
from django.utils import timezone

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:
    BackgroundScheduler = None

from dashboard.models import ActivityReport, User, Notification


def get_foremen_without_report(today, target_shift=None):
    foremen_qs = User.objects.filter(role='foreman', is_active=True)
    if target_shift:
        foremen_qs = foremen_qs.filter(shift=target_shift)

    missing = []
    for foreman in foremen_qs:
        has_report_today = ActivityReport.objects.filter(
            foreman=foreman,
            date=today
        ).exists()
        if not has_report_today:
            missing.append(foreman)
    return missing


def send_pre_deadline_reminders(target_shift):
    today = timezone.localdate()
    recipients = get_foremen_without_report(today, target_shift=target_shift)
    if not recipients:
        return 0

    # Compose message per shift
    if target_shift == 1:
        deadline_str = "18:00"
        shift_name = "Shift 1"
    else:
        deadline_str = "05:00"
        shift_name = "Shift 2"

    title = "🔔 Pengingat Activity Report (H-1 Jam)"
    message = (
        f"Pengingat otomatis: Anda belum mengisi Activity Report untuk tanggal "
        f"{today.strftime('%d %B %Y')}. Batas waktu {shift_name} adalah {deadline_str}. "
        f"Mohon segera isi sebelum lewat waktu."
    )

    Notification.create_broadcast_notification(
        title=title,
        message=message,
        recipients=recipients,
        created_by=None,  # Sistem
    )
    return len(recipients)


class Command(BaseCommand):
    help = "Run APScheduler to send automatic pre-deadline notifications to foremen."

    def handle(self, *args, **options):
        if BackgroundScheduler is None:
            self.stderr.write(
                self.style.ERROR(
                    "APScheduler not installed. Please ensure 'APScheduler' and 'django-apscheduler' are installed."
                )
            )
            return

        scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))

        # Send immediately at start (useful after restarts)
        sent_shift1 = send_pre_deadline_reminders(target_shift=1)
        sent_shift2 = send_pre_deadline_reminders(target_shift=2)
        self.stdout.write(self.style.SUCCESS(
            f"Startup reminders sent: Shift1={sent_shift1}, Shift2={sent_shift2}"
        ))

        # Schedule daily reminders 1 hour before deadlines
        # Shift 1 deadline at 18:00 -> reminder at 17:00 local time
        scheduler.add_job(
            lambda: self._run_and_log(1),
            'cron', hour=17, minute=0, id='pre_deadline_shift1', replace_existing=True
        )
        # Shift 2 deadline at 05:00 -> reminder at 04:00 local time
        scheduler.add_job(
            lambda: self._run_and_log(2),
            'cron', hour=4, minute=0, id='pre_deadline_shift2', replace_existing=True
        )

        self.stdout.write(self.style.SUCCESS("Notification scheduler started. Running in background..."))

        try:
            scheduler.start()
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.WARNING("Notification scheduler stopped."))

    def _run_and_log(self, shift):
        count = send_pre_deadline_reminders(target_shift=shift)
        self.stdout.write(self.style.SUCCESS(f"Pre-deadline reminders sent for Shift {shift}: {count}"))