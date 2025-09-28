from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard.models import User, ActivityReport, ActivityReportDetail, AnalysisReport, LeaderQuota
from datetime import datetime, timedelta, time
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate new dummy data with updated schema'

    def handle(self, *args, **options):
        self.stdout.write('Generating new dummy data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        ActivityReportDetail.objects.all().delete()
        ActivityReport.objects.all().delete()
        AnalysisReport.objects.all().delete()
        LeaderQuota.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create Leaders with Quotas
        self.stdout.write('Creating leaders...')
        leaders_data = [
            {'name': 'Ahmad Supervisor', 'username': 'ahmad_leader', 'email': 'ahmad@company.com', 'department': 'SUPPORT', 'max_foreman': 3},
            {'name': 'Budi Manager', 'username': 'budi_leader', 'email': 'budi@company.com', 'department': 'TRACK', 'max_foreman': 4},
            {'name': 'Citra Koordinator', 'username': 'citra_leader', 'email': 'citra@company.com', 'department': 'PLANT', 'max_foreman': 2},
            {'name': 'Dedi Supervisor', 'username': 'dedi_leader', 'email': 'dedi@company.com', 'department': 'WHEEL', 'max_foreman': 3},
        ]
        
        leaders = []
        for leader_data in leaders_data:
            # Create LeaderQuota first
            quota = LeaderQuota.objects.create(
                leader_name=leader_data['name'],
                leader_username=leader_data['username'],
                max_foreman=leader_data['max_foreman'],
                current_foreman_count=0,
                is_active=True
            )
            
            # Create Leader User
            leader = User.objects.create_user(
                username=leader_data['username'],
                email=leader_data['email'],
                password='password123',
                name=leader_data['name'],
                role='leader',
                department=leader_data['department'],
                shift=random.choice([1, 2]),
                nrp=f"L{random.randint(1000, 9999)}",
                phone=f"08{random.randint(10000000, 99999999)}"
            )
            
            # Link quota to user
            quota.leader_user = leader
            quota.save()
            
            leaders.append(leader)
            self.stdout.write(f'Created leader: {leader.name}')
        
        # Create Foremen
        self.stdout.write('Creating foremen...')
        foremen_data = [
            {'name': 'Eko Foreman', 'username': 'eko_foreman', 'email': 'eko@company.com'},
            {'name': 'Fajar Operator', 'username': 'fajar_foreman', 'email': 'fajar@company.com'},
            {'name': 'Gita Teknisi', 'username': 'gita_foreman', 'email': 'gita@company.com'},
            {'name': 'Hadi Mekanik', 'username': 'hadi_foreman', 'email': 'hadi@company.com'},
            {'name': 'Indra Operator', 'username': 'indra_foreman', 'email': 'indra@company.com'},
            {'name': 'Joko Teknisi', 'username': 'joko_foreman', 'email': 'joko@company.com'},
            {'name': 'Kiki Mekanik', 'username': 'kiki_foreman', 'email': 'kiki@company.com'},
            {'name': 'Lina Operator', 'username': 'lina_foreman', 'email': 'lina@company.com'},
        ]
        
        foremen = []
        for i, foreman_data in enumerate(foremen_data):
            # Assign to leader with available quota
            leader = leaders[i % len(leaders)]
            # Get the quota object for this leader
            quota = LeaderQuota.objects.get(leader_user=leader)
            if quota.can_add_foreman():
                foreman = User.objects.create_user(
                    username=foreman_data['username'],
                    email=foreman_data['email'],
                    password='password123',
                    name=foreman_data['name'],
                    role='foreman',
                    department=leader.department,
                    shift=random.choice([1, 2]),
                    nrp=f"F{random.randint(1000, 9999)}",
                    phone=f"08{random.randint(10000000, 99999999)}",
                    leader=leader
                )
                
                # Update leader quota count
                quota.current_foreman_count += 1
                quota.save()
                
                foremen.append(foreman)
                self.stdout.write(f'Created foreman: {foreman.name} under {leader.name}')
        
        # Create Admin
        admin = User.objects.create_user(
            username='admin',
            email='admin@company.com',
            password='password123',
            name='System Admin',
            role='admin',
            department='SUPPORT',
            shift=1,
            nrp='A0001',
            phone='081234567890'
        )
        self.stdout.write('Created admin user')
        
        # Generate Activity Reports with new structure
        self.stdout.write('Creating activity reports...')
        sections = [choice[0] for choice in ActivityReport.SECTION_CHOICES]
        components = [choice[0] for choice in ActivityReport.COMPONENT_CHOICES]
        activities_codes = [choice[0] for choice in ActivityReport.ACTIVITIES_CHOICES]
        
        activities_list = [
            'Pemeriksaan rutin engine dan sistem pendingin',
            'Penggantian oli mesin dan filter udara',
            'Perbaikan sistem hidrolik dan pneumatic',
            'Maintenance berkala komponen undercarriage',
            'Inspeksi dan perbaikan sistem kelistrikan',
            'Penggantian spare part yang rusak',
            'Kalibrasi sistem kontrol dan sensor',
            'Pembersihan dan pelumasan komponen mesin'
        ]
        
        for foreman in foremen:
            # Create 3-7 activity reports per foreman
            for i in range(random.randint(3, 7)):
                date = timezone.now().date() - timedelta(days=random.randint(0, 30))
                
                # Create main activity report with new structure
                activity_report = ActivityReport.objects.create(
                    foreman=foreman,
                    nrp=foreman.nrp,
                    section=random.choice(sections),
                    date=date,
                    status=random.choice(['pending', 'approved', 'rejected']),
                    feedback='Good work' if random.choice([True, False]) else ''
                )
                
                # Create 1-5 activity details for each report
                num_activities = random.randint(1, 5)
                for activity_num in range(1, num_activities + 1):
                    start_time = time(random.randint(6, 10), random.randint(0, 59))
                    # End time 1-4 hours later
                    start_datetime = datetime.combine(date, start_time)
                    end_datetime = start_datetime + timedelta(hours=random.randint(1, 4))
                    end_time = end_datetime.time()
                    
                    ActivityReportDetail.objects.create(
                        activity_report=activity_report,
                        activity_number=activity_num,
                        unit_code=f"UN{random.randint(100, 999)}",
                        hm_km=f"{random.randint(1000, 9999)} HM",
                        start_time=start_time,
                        stop_time=end_time,
                        component=random.choice(components),
                        activities=random.choice(activities_list),
                        activity_code=random.choice(activities_codes)
                    )
        
        # Generate Analysis Reports (unchanged as they don't use the new structure)
        self.stdout.write('Creating analysis reports...')
        problems = ['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000']
        sections = ['PC1250', 'CAT395', 'DX800', 'PC500', 'PC300', 'PC200/210', 'D375', 'D155', 'D85', 'EPIROC DM30']
        
        problem_titles = [
            'Engine overheating pada unit excavator',
            'Kebocoran oli hidrolik pada sistem boom',
            'Kerusakan track chain dan sprocket',
            'Masalah pada sistem kelistrikan alternator',
            'Penurunan performa engine dan fuel consumption tinggi',
            'Kerusakan pada sistem pendingin radiator',
            'Masalah pada transmisi dan final drive',
            'Kerusakan komponen undercarriage'
        ]
        
        for foreman in foremen:
            # Create 2-5 analysis reports per foreman
            for i in range(random.randint(2, 5)):
                report_date = timezone.now().date() - timedelta(days=random.randint(0, 60))
                wo_date = report_date - timedelta(days=random.randint(1, 5))
                trouble_date = report_date - timedelta(days=random.randint(1, 10))
                
                AnalysisReport.objects.create(
                    foreman=foreman,
                    section_track=random.choice(sections),
                    email=foreman.email,
                    no_report=f"AR{random.randint(1000, 9999)}",
                    report_date=report_date,
                    WO_Number=f"WO{random.randint(10000, 99999)}",
                    WO_date=wo_date,
                    unit_code=f"UN{random.randint(100, 999)}",
                    problem=random.choice(problems),
                    Trouble_date=trouble_date,
                    Hm=f"{random.randint(1000, 9999)}",
                    title_problem=random.choice(problem_titles),
                    part_no=f"PN{random.randint(10000, 99999)}",
                    part_name=f"Spare Part {random.randint(1, 100)}",
                    status=random.choice(['pending', 'approved', 'rejected']),
                    feedback='Analysis completed' if random.choice([True, False]) else '',
                    # Extended fields
                    nama_fungsi_komponen=f"Komponen {random.choice(['Engine', 'Hydraulic', 'Transmission', 'Electrical'])} berfungsi untuk operasional utama",
                    gejala_masalah=f"Gejala yang terlihat: {random.choice(['suara tidak normal', 'kebocoran', 'overheating', 'performa menurun'])}",
                    akar_penyebab_masalah=f"Penyebab utama: {random.choice(['wear and tear', 'kurang maintenance', 'overload', 'kontaminasi'])}",
                    faktor_man=f"Faktor manusia: {random.choice(['Kelalaian operator', 'Kurang training', 'Tidak mengikuti SOP', 'Tidak ada masalah'])}",
                    faktor_material=f"Faktor material: {random.choice(['Material tidak sesuai spec', 'Kualitas rendah', 'Kontaminasi', 'Tidak ada masalah'])}",
                    faktor_machine=f"Faktor mesin: {random.choice(['Wear normal', 'Overload', 'Kurang maintenance', 'Tidak ada masalah'])}",
                    faktor_method=f"Faktor metode: {random.choice(['SOP tidak sesuai', 'Metode kerja salah', 'Tidak ada panduan', 'Tidak ada masalah'])}",
                    faktor_environment=f"Faktor lingkungan: {random.choice(['Kondisi ekstrem', 'Debu berlebih', 'Suhu tinggi', 'Tidak ada masalah'])}",
                    tindakan_dilakukan=f"Tindakan: {random.choice(['penggantian part', 'perbaikan', 'adjustment', 'cleaning'])}",
                    tindakan_pencegahan=f"Pencegahan: {random.choice(['maintenance rutin', 'monitoring berkala', 'training operator', 'upgrade sistem'])}"
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully generated new dummy data!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'- {len(leaders)} Leaders')
        self.stdout.write(f'- {len(foremen)} Foremen')
        self.stdout.write(f'- 1 Admin')
        self.stdout.write(f'- {ActivityReport.objects.count()} Activity Reports')
        self.stdout.write(f'- {ActivityReportDetail.objects.count()} Activity Report Details')
        self.stdout.write(f'- {AnalysisReport.objects.count()} Analysis Reports')
        self.stdout.write(f'- {LeaderQuota.objects.count()} Leader Quotas')
        self.stdout.write('All users have password: password123')
        
        # Generate Analysis Reports
        self.stdout.write('Creating analysis reports...')
        problems = ['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000']
        sections = ['PC1250', 'CAT395', 'DX800', 'PC500', 'PC300', 'PC200/210', 'D375', 'D155', 'D85', 'EPIROC DM30']
        
        problem_titles = [
            'Engine overheating pada unit excavator',
            'Kebocoran oli hidrolik pada sistem boom',
            'Kerusakan track chain dan sprocket',
            'Masalah pada sistem kelistrikan alternator',
            'Penurunan performa engine dan fuel consumption tinggi',
            'Kerusakan pada sistem pendingin radiator',
            'Masalah pada transmisi dan final drive',
            'Kerusakan komponen undercarriage'
        ]
        
        for foreman in foremen:
            # Create 2-5 analysis reports per foreman
            for i in range(random.randint(2, 5)):
                report_date = timezone.now().date() - timedelta(days=random.randint(0, 60))
                wo_date = report_date - timedelta(days=random.randint(1, 5))
                trouble_date = report_date - timedelta(days=random.randint(1, 10))
                
                AnalysisReport.objects.create(
                    foreman=foreman,
                    section_track=random.choice(sections),
                    email=foreman.email,
                    no_report=f"AR{random.randint(1000, 9999)}",
                    report_date=report_date,
                    WO_Number=f"WO{random.randint(10000, 99999)}",
                    WO_date=wo_date,
                    unit_code=f"UN{random.randint(100, 999)}",
                    problem=random.choice(problems),
                    Trouble_date=trouble_date,
                    Hm=f"{random.randint(1000, 9999)}",
                    title_problem=random.choice(problem_titles),
                    part_no=f"PN{random.randint(10000, 99999)}",
                    part_name=f"Spare Part {random.randint(1, 100)}",
                    status=random.choice(['pending', 'approved', 'rejected']),
                    feedback='Analysis completed' if random.choice([True, False]) else '',
                    # Extended fields
                    nama_fungsi_komponen=f"Komponen {random.choice(['Engine', 'Hydraulic', 'Transmission', 'Electrical'])} berfungsi untuk operasional utama",
                    gejala_masalah=f"Gejala yang terlihat: {random.choice(['suara tidak normal', 'kebocoran', 'overheating', 'performa menurun'])}",
                    akar_penyebab_masalah=f"Penyebab utama: {random.choice(['wear and tear', 'kurang maintenance', 'overload', 'kontaminasi'])}",
                    faktor_man=random.choice([True, False]),
                    faktor_material=random.choice([True, False]),
                    faktor_machine=random.choice([True, False]),
                    faktor_method=random.choice([True, False]),
                    faktor_environment=random.choice([True, False]),
                    tindakan_dilakukan=f"Tindakan: {random.choice(['penggantian part', 'perbaikan', 'adjustment', 'cleaning'])}",
                    tindakan_pencegahan=f"Pencegahan: {random.choice(['maintenance rutin', 'monitoring berkala', 'training operator', 'upgrade sistem'])}"
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully generated new dummy data!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'- {len(leaders)} Leaders')
        self.stdout.write(f'- {len(foremen)} Foremen')
        self.stdout.write(f'- 1 Admin')
        self.stdout.write(f'- {ActivityReport.objects.count()} Activity Reports')
        self.stdout.write(f'- {AnalysisReport.objects.count()} Analysis Reports')
        self.stdout.write(f'- {LeaderQuota.objects.count()} Leader Quotas')