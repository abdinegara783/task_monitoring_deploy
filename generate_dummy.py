
#!/usr/bin/env python
"""
Script untuk generate data dummy
Jalankan dari root directory project: python generate_dummy.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import random
from datetime import datetime, timedelta, time
from django.contrib.auth.hashers import make_password
from dashboard.models import User, ActivityReport

def create_dummy_users(count=20):
    """Create dummy users"""
    print(f"Creating {count} dummy users...")
    
    departments = ['SUPPORT', 'TRACK', 'PLANT', 'WHEEL']
    roles = ['foreman', 'leader', 'admin']
    
    # Sample Indonesian names
    first_names = [
        'Ahmad', 'Budi', 'Candra', 'Dedi', 'Eko', 'Fajar', 'Gunawan', 'Hadi',
        'Indra', 'Joko', 'Kurnia', 'Lukman', 'Maman', 'Nanda', 'Oki', 'Putra',
        'Qomar', 'Rizki', 'Sandi', 'Tono', 'Udin', 'Vino', 'Wahyu', 'Yudi', 'Zaki'
    ]
    
    last_names = [
        'Santoso', 'Pratama', 'Wijaya', 'Kusuma', 'Permana', 'Saputra', 'Nugroho',
        'Hidayat', 'Setiawan', 'Raharjo', 'Susanto', 'Wibowo', 'Kurniawan', 'Sari',
        'Lestari', 'Handayani', 'Maharani', 'Puspita', 'Anggraini', 'Safitri'
    ]
    
    users_created = 0
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@company.com"
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            continue
        
        user = User.objects.create(
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
            password=make_password('password123'),
            is_active=True,
        )
        users_created += 1
        
        if users_created % 5 == 0:
            print(f"Created {users_created} users...")
    
    print(f"✅ Successfully created {users_created} users")
    return users_created

def create_dummy_activity_reports(count=50):
    """Create dummy activity reports"""
    print(f"Creating {count} dummy activity reports...")
    
    # Get foreman users
    foreman_users = list(User.objects.filter(role='foreman'))
    
    if not foreman_users:
        print("❌ No foreman users found. Please create users first.")
        return 0
    
    leaders = [choice[0] for choice in ActivityReport.LEADER_CHOICES]
    components = [choice[0] for choice in ActivityReport.COMPONENT_CHOICES]
    activities_codes = [choice[0] for choice in ActivityReport.ACTIVITIES_CHOICES]
    
    activities_descriptions = [
        "Melakukan pemeriksaan rutin pada engine unit EX1200",
        "Penggantian oli hydraulic dan filter pada unit HD785",
        "Perbaikan sistem kelistrikan pada excavator PC400",
        "Maintenance berkala pada sistem transmisi dump truck",
        "Pemeriksaan dan penyesuaian brake system unit HD1500",
        "Cleaning dan greasing pada under carriage excavator",
        "Pengecekan kondisi ban dan tekanan angin dump truck",
        "Perbaikan minor pada sistem steering unit HD785",
        "Pemeriksaan kondisi attachment bucket dan GET",
        "Service berkala 250 jam operasi pada unit EX2500",
        "Penggantian komponen yang aus pada final drive",
        "Pemeriksaan sistem pneumatic dan air brake",
        "Maintenance AC dan sistem pendingin cabin",
        "Pemeriksaan frame dan guard unit untuk keamanan",
        "Service PTO dan coupling system pada unit support",
        "Overhaul engine komponen mayor pada unit EX1900",
        "Penggantian track shoe pada excavator PC1250",
        "Pemeriksaan sistem hydraulic dan pressure test",
        "Service transmisi dan final drive unit HD1500",
        "Maintenance berkala sistem electrical dan wiring",
    ]
    
    reports_created = 0
    
    for i in range(count):
        # Random date within last 3 months
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Random start and end time
        start_hour = random.randint(6, 14)  # 6 AM to 2 PM
        start_minute = random.choice([0, 15, 30, 45])
        start_time = time(start_hour, start_minute)
        
        # End time 4-8 hours after start
        duration_hours = random.randint(4, 8)
        end_datetime = datetime.combine(random_date.date(), start_time) + timedelta(hours=duration_hours)
        end_time = end_datetime.time()
        
        ActivityReport.objects.create(
            foreman=random.choice(foreman_users),
            date=random_date.date(),
            shift=random.choice([1, 2]),
            start_time=start_time,
            end_time=end_time,
            activities=random.choice(activities_descriptions),
            leader=random.choice(leaders),
            Unit_Code=f"UNIT{random.randint(100, 999)}",
            Hmkm=f"{random.randint(1000, 9999)} HM",
            component=random.choice(components),
            activities_code=random.choice(activities_codes),
        )
        reports_created += 1
        
        if reports_created % 10 == 0:
            print(f"Created {reports_created} activity reports...")
    
    print(f"✅ Successfully created {reports_created} activity reports")
    return reports_created

def main():
    print("🚀 Starting dummy data generation...")
    print("="*50)
    
    # Create users first
    users_count = create_dummy_users(25)
    
    # Create activity reports
    reports_count = create_dummy_activity_reports(75)
    
    print("="*50)
    print(f"🎉 Data generation completed!")
    print(f"📊 Summary:")
    print(f"   - Users created: {users_count}")
    print(f"   - Activity reports created: {reports_count}")
    print(f"")
    print(f"🔑 Default password for all users: password123")
    print(f"📝 You can now login with any username and password123")

if __name__ == '__main__':
    main()