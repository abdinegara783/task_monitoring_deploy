import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from dashboard.models import User, ActivityReport
from faker import Faker

class Command(BaseCommand):
    help = 'Generate dummy data without resetting database'
    
    def __init__(self):
        super().__init__()
        self.fake = Faker('id_ID')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--reports',
            type=int,
            default=25,
            help='Number of activity reports to create (default: 25)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing non-superuser data before generating'
        )
    
    def handle(self, *args, **options):
        if options['clear_existing']:
            self.stdout.write('🗑️  Clearing existing data...')
            ActivityReport.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write('   ✅ Existing data cleared')
        
        self.stdout.write('📊 Generating additional data...')
        
        # Generate users
        users_created = self.create_users(options['users'])
        
        # Generate reports
        reports_created = self.create_activity_reports(options['reports'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully added {users_created} users and {reports_created} reports'
            )
        )
    
    def create_users(self, count):
        # Same implementation as reset_and_generate.py
        # ... (copy the create_users method from above)
        pass
    
    def create_activity_reports(self, count):
        # Same implementation as reset_and_generate.py
        # ... (copy the create_activity_reports method from above)
        pass