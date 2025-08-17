from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from dashboard.models import User, ActivityReport, AnalysisReport, Notification
import calendar

class Command(BaseCommand):
    help = 'Send automatic notifications for activity and analysis reports'
    
    def handle(self, *args, **options):
        self.stdout.write('🔔 Checking for notification triggers...')
        
        # Check activity report reminders
        self.check_activity_reminders()
        
        # Check analysis report reminders
        self.check_analysis_reminders()
        
        self.stdout.write('✅ Notification check completed')
    
    def check_activity_reminders(self):
        """Check and send activity report reminders"""
        now = timezone.now()
        today = now.date()
        
        # Deadline is 18:00 (6 PM)
        deadline_time = datetime.combine(today, datetime.min.time().replace(hour=18))
        deadline_time = timezone.make_aware(deadline_time)
        
        # Skip if deadline has passed
        if now > deadline_time:
            return
        
        # Calculate hours until deadline
        time_until_deadline = deadline_time - now
        hours_left = time_until_deadline.total_seconds() / 3600
        
        # Get all foreman users
        foreman_users = User.objects.filter(role='foreman', is_active=True)
        
        for user in foreman_users:
            # Check if user has already submitted activity report today
            has_report_today = ActivityReport.objects.filter(
                foreman=user,
                date=today
            ).exists()
            
            if not has_report_today:
                # Send reminders at specific intervals
                if 0.9 <= hours_left <= 1.1:  # 1 hour before (with 6-minute tolerance)
                    notification = Notification.create_activity_reminder(user, 1)
                    if notification:
                        self.stdout.write(f'📧 Sent 1-hour reminder to {user.username}')
                
                elif 0.4 <= hours_left <= 0.6:  # 30 minutes before
                    notification = Notification.create_activity_reminder(user, 0.5)
                    if notification:
                        self.stdout.write(f'🚨 Sent 30-minute reminder to {user.username}')
                
                elif 0.1 <= hours_left <= 0.2:  # 10 minutes before
                    notification = Notification.create_activity_reminder(user, 1/6)
                    if notification:
                        self.stdout.write(f'🔥 Sent 10-minute URGENT reminder to {user.username}')
    
    def check_analysis_reminders(self):
        """Check and send analysis report reminders"""
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Get last day of current month
        last_day = calendar.monthrange(current_year, current_month)[1]
        month_end = datetime(current_year, current_month, last_day, 23, 59, 59)
        month_end = timezone.make_aware(month_end)
        
        # Calculate days until month end
        days_until_end = (month_end - now).days
        
        # Send reminder 3 days before month end
        if days_until_end == 3:
            foreman_users = User.objects.filter(role='foreman', is_active=True)
            
            for user in foreman_users:
                # Count analysis reports this month
                reports_this_month = AnalysisReport.objects.filter(
                    foreman=user,
                    month=current_month,
                    year=current_year
                ).count()
                
                # Required: 3 reports per month
                required_reports = 3
                missing_count = required_reports - reports_this_month
                
                if missing_count > 0:
                    notification = Notification.create_analysis_reminder(
                        user, 3, missing_count
                    )
                    if notification:
                        self.stdout.write(
                            f'📊 Sent analysis reminder to {user.username} '
                            f'({missing_count} reports missing)'
                        )