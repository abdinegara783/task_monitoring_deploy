from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from dashboard.models import User, ShiftSchedule


class Command(BaseCommand):
    help = "Generate 7-day shift schedules for all foremen in a round-robin: Shift1, Shift2, Stop."

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            type=str,
            help="Start date in YYYY-MM-DD (default: today)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days to generate (default: 7)",
        )
        parser.add_argument(
            "--department",
            type=str,
            default="mechanic",
            help="Department name to set on schedules (default: mechanic)",
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        start_date = today
        if options.get("start"):
            try:
                start_date = timezone.datetime.strptime(options["start"], "%Y-%m-%d").date()
            except ValueError:
                self.stderr.write(self.style.ERROR("Invalid --start date format. Use YYYY-MM-DD."))
                return

        days = options["days"]
        department = options["department"]
        foremen = User.objects.filter(role="foreman").order_by("id")

        if not foremen.exists():
            self.stdout.write(self.style.WARNING("No foremen found. Nothing to schedule."))
            return

        cycle = [1, 2, 0]  # Shift1, Shift2, Stop

        created_count = 0
        updated_count = 0

        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            for idx, foreman in enumerate(foremen):
                shift_val = cycle[(idx + day_offset) % len(cycle)]

                obj, created = ShiftSchedule.objects.update_or_create(
                    date=date,
                    foreman=foreman,
                    defaults={
                        "department": department,
                        "shift": shift_val,
                        "is_active": True,
                        "notes": "Auto-generated",
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated schedules for {days} day(s). Created: {created_count}, Updated: {updated_count}."
            )
        )