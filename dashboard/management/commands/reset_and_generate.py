import os
import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import connection, transaction
from django.conf import settings
from dashboard.models import User, ActivityReport, ActivityReportDetail
from faker import Faker


class Command(BaseCommand):
    help = "Reset database and generate fresh dummy data with new ActivityReport structure"

    def __init__(self):
        super().__init__()
        self.fake = Faker("id_ID")

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=25,
            help="Number of users to create (default: 25)",
        )
        parser.add_argument(
            "--reports",
            type=int,
            default=30,
            help="Number of activity reports to create (default: 30)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reset even if database is locked",
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write("🚀 Starting database reset and data generation...")
            self.stdout.write("=" * 60)

            # Step 1: Reset Database
            self.reset_database_safe(options["force"])

            # Step 2: Run Migrations
            self.run_migrations()

            # Step 3: Generate Users
            self.stdout.write("\n📊 Generating users...")
            users_created = self.create_users_safe(options["users"])

            # Step 4: Generate Activity Reports with Details
            self.stdout.write("\n📋 Generating activity reports...")
            reports_created = self.create_activity_reports_safe(options["reports"])

            # Step 5: Summary
            self.print_summary(users_created, reports_created)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error occurred: {str(e)}"))
            self.stdout.write("\n🔧 Try running with --force flag or manual reset:")
            self.stdout.write("   rm backend/db.sqlite3")
            self.stdout.write("   python manage.py migrate")
            self.stdout.write("   python manage.py reset_and_generate")

    def reset_database_safe(self, force=False):
        """Safely reset database with error handling"""
        self.stdout.write("🗑️  Resetting database...")

        try:
            # Close all database connections
            connection.close()

            # Get database path
            db_path = settings.DATABASES["default"]["NAME"]

            # Force close any remaining connections
            if force:
                import sqlite3

                try:
                    # Try to connect and close immediately to release locks
                    conn = sqlite3.connect(db_path, timeout=1)
                    conn.close()
                except:
                    pass

            # Delete database file if it exists
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    self.stdout.write("   ✅ Database file deleted")
                except PermissionError:
                    self.stdout.write(
                        "   ⚠️  Database file is locked, trying alternative method..."
                    )
                    # Alternative: rename and create new
                    backup_name = f"{db_path}.backup_{int(datetime.now().timestamp())}"
                    os.rename(db_path, backup_name)
                    self.stdout.write(f"   ✅ Database backed up as {backup_name}")
            else:
                self.stdout.write("   ℹ️  Database file not found, creating new one")

        except Exception as e:
            self.stdout.write(f"   ⚠️  Warning during database reset: {str(e)}")

    def run_migrations(self):
        """Run Django migrations with error handling"""
        self.stdout.write("🔄 Running migrations...")

        try:
            from django.core.management import call_command

            # Make migrations first
            call_command("makemigrations", "dashboard", verbosity=0, interactive=False)

            # Run migrations
            call_command("migrate", verbosity=0, interactive=False)
            self.stdout.write("   ✅ Migrations completed")

        except Exception as e:
            self.stdout.write(f"   ❌ Migration error: {str(e)}")
            raise

    @transaction.atomic
    def create_users_safe(self, count):
        """Create users with transaction safety"""
        try:
            departments = ["SUPPORT", "TRACK", "PLANT", "WHEEL"]
            roles = ["foreman", "leader", "admin"]

            first_names = [
                "Ahmad", "Budi", "Candra", "Dedi", "Eko", "Fajar", "Gunawan", 
                "Hadi", "Indra", "Joko", "Kurnia", "Lukman", "Maman", "Nanda", 
                "Oki", "Putra", "Qomar", "Rizki", "Sandi", "Tono", "Udin", 
                "Vino", "Wahyu", "Yudi", "Zaki",
            ]

            last_names = [
                "Santoso", "Pratama", "Wijaya", "Kusuma", "Permana", "Saputra", 
                "Nugroho", "Hidayat", "Setiawan", "Raharjo", "Susanto", "Wibowo", 
                "Kurniawan",
            ]

            users_created = 0
            batch_size = 10  # Create in smaller batches

            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                users_batch = []

                for i in range(batch_start, batch_end):
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
                    email = f"{username}@company.com"

                    # Check for duplicates
                    if User.objects.filter(username=username).exists():
                        username = f"{username}_{random.randint(1000, 9999)}"
                        email = f"{username}@company.com"

                    user_data = User(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        name=f"{first_name} {last_name}",
                        phone=f"08{random.randint(10000000, 99999999)}",
                        nrp=f"NRP{random.randint(10000, 99999)}",
                        role=random.choice(roles),
                        department=random.choice(departments),
                        shift=random.choice([1, 2]),
                        password=make_password("password123"),
                        is_active=True,
                    )
                    users_batch.append(user_data)

                # Bulk create batch
                User.objects.bulk_create(users_batch, ignore_conflicts=True)
                users_created += len(users_batch)

                self.stdout.write(
                    f"   📝 Created {users_created}/{count} users...", ending="\r"
                )

            self.stdout.write(f"   ✅ Successfully created {users_created} users")
            return users_created

        except Exception as e:
            self.stdout.write(f"   ❌ Error creating users: {str(e)}")
            raise

    @transaction.atomic
    def create_activity_reports_safe(self, count):
        """Create activity reports with new structure"""
        try:
            # Get foreman users
            foreman_users = list(User.objects.filter(role="foreman"))

            if not foreman_users:
                self.stdout.write("   ⚠️  No foreman users found. Creating some...")
                # Create foreman users
                for i in range(5):
                    User.objects.create(
                        username=f"foreman{i + 1}",
                        email=f"foreman{i + 1}@company.com",
                        first_name="Foreman",
                        last_name=f"{i + 1}",
                        name=f"Foreman {i + 1}",
                        nrp=f"NRP{random.randint(10000, 99999)}",
                        role="foreman",
                        department=random.choice(["SUPPORT", "TRACK", "PLANT", "WHEEL"]),
                        shift=random.choice([1, 2]),
                        password=make_password("password123"),
                    )
                foreman_users = list(User.objects.filter(role="foreman"))

            sections = [choice[0] for choice in ActivityReport.SECTION_CHOICES]
            components = [choice[0] for choice in ActivityReport.COMPONENT_CHOICES]
            activities_codes = [choice[0] for choice in ActivityReport.ACTIVITIES_CHOICES]

            activities_descriptions = [
                "Pemeriksaan rutin engine unit - oil level dan coolant check",
                "Penggantian oli hydraulic - scheduled maintenance",
                "Perbaikan sistem kelistrikan - troubleshooting",
                "Maintenance transmisi - oil change dan adjustment",
                "Pemeriksaan brake system - pad inspection",
                "Cleaning under carriage - track maintenance",
                "Pengecekan kondisi ban - pressure check",
                "Service steering system - fluid check",
                "Pemeriksaan attachment - wear parts inspection",
                "Service berkala 500 jam - comprehensive check",
            ]

            reports_created = 0
            activities_created = 0

            for i in range(count):
                foreman = random.choice(foreman_users)
                
                # Random date within last 2 months
                report_date = self.fake.date_between(start_date="-2M", end_date="today")
                
                # Create main activity report
                activity_report = ActivityReport.objects.create(
                    foreman=foreman,
                    nrp=foreman.nrp or f"NRP{random.randint(10000, 99999)}",
                    section=random.choice(sections),
                    date=report_date,
                    status="pending"
                )
                
                # Create 1-5 activity details for each report
                num_activities = random.randint(1, 5)
                
                for activity_num in range(1, num_activities + 1):
                    # Random working hours
                    start_hour = random.randint(7, 13)
                    start_time = time(start_hour, random.choice([0, 30]))
                    
                    # End time 1-4 hours later
                    duration = random.randint(1, 4)
                    end_datetime = datetime.combine(report_date, start_time) + timedelta(hours=duration)
                    end_time = end_datetime.time()
                    
                    ActivityReportDetail.objects.create(
                        activity_report=activity_report,
                        activity_number=activity_num,
                        unit_code=f"UNIT{random.randint(100, 999)}",
                        hm_km=f"{random.randint(1000, 9999)} HM",
                        start_time=start_time,
                        stop_time=end_time,
                        component=random.choice(components),
                        activities=random.choice(activities_descriptions),
                        activity_code=random.choice(activities_codes)
                    )
                    activities_created += 1
                
                reports_created += 1
                
                self.stdout.write(
                    f"   📋 Created {reports_created}/{count} reports ({activities_created} activities)...", 
                    ending="\r"
                )

            self.stdout.write(
                f"   ✅ Successfully created {reports_created} activity reports with {activities_created} activities"
            )
            return reports_created

        except Exception as e:
            self.stdout.write(f"   ❌ Error creating reports: {str(e)}")
            raise

    def print_summary(self, users_created, reports_created):
        """Print generation summary"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎉 Database reset and data generation completed!")
        self.stdout.write("\n📊 Summary:")
        self.stdout.write(f"   👥 Users created: {users_created}")
        self.stdout.write(f"   📋 Activity reports created: {reports_created}")
        
        # Count total activities
        total_activities = ActivityReportDetail.objects.count()
        self.stdout.write(f"   🔧 Total activities created: {total_activities}")
        
        self.stdout.write("\n🔑 Login Information:")
        self.stdout.write("   📧 Any username with password: password123")
        self.stdout.write("   🌐 Access: http://127.0.0.1:8000/login/")
        self.stdout.write("\n🚀 Ready to use the new Activity Report system!")
        self.stdout.write("\n📝 New Features:")
        self.stdout.write("   • Multi-step form with NRP, Section, Date")
        self.stdout.write("   • Up to 5 activities per report")
        self.stdout.write("   • Individual activity details with time tracking")
        self.stdout.write("   • Enhanced admin interface with inline editing")
