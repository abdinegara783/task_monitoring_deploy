from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from dashboard.models import User, LeaderQuota, ActivityReport
from datetime import date, time

class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data...')
        
        # 1. Buat superadmin
        superadmin, created = User.objects.get_or_create(
            username='superadmin',
            defaults={
                'email': 'superadmin@monman.com',
                'password': make_password('admin123'),
                'role': 'superadmin',
                'name': 'Super Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created superadmin: {superadmin.username}')
        
        # 2. Buat admin
        admin, created = User.objects.get_or_create(
            username='admin1',
            defaults={
                'email': 'admin1@monman.com',
                'password': make_password('admin123'),
                'role': 'admin',
                'name': 'Admin Utama',
                'department': 'SUPPORT'
            }
        )
        if created:
            self.stdout.write(f'✓ Created admin: {admin.username}')
        
        # 3. Buat LeaderQuota untuk setiap leader
        leader_quotas = [
            {'leader_name': 'Leader_1', 'max_foreman': 5},
            {'leader_name': 'Leader_2', 'max_foreman': 4},
            {'leader_name': 'Leader_3', 'max_foreman': 3},
            {'leader_name': 'Leader_4', 'max_foreman': 6},
        ]
        
        for quota_data in leader_quotas:
            quota, created = LeaderQuota.objects.get_or_create(
                leader_name=quota_data['leader_name'],
                defaults={
                    'max_foreman': quota_data['max_foreman'],
                    'current_foreman_count': 0,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✓ Created quota for {quota.leader_name}')
        
        # 4. Buat leaders
        leaders_data = [
            {'username': 'leader1', 'name': 'Leader Satu', 'quota_name': 'Leader_1', 'dept': 'SUPPORT'},
            {'username': 'leader2', 'name': 'Leader Dua', 'quota_name': 'Leader_2', 'dept': 'TRACK'},
            {'username': 'leader3', 'name': 'Leader Tiga', 'quota_name': 'Leader_3', 'dept': 'PLANT'},
            {'username': 'leader4', 'name': 'Leader Empat', 'quota_name': 'Leader_4', 'dept': 'WHEEL'},
        ]
        
        leaders = []
        for leader_data in leaders_data:
            quota = LeaderQuota.objects.get(leader_name=leader_data['quota_name'])
            leader, created = User.objects.get_or_create(
                username=leader_data['username'],
                defaults={
                    'email': f"{leader_data['username']}@monman.com",
                    'password': make_password('leader123'),
                    'role': 'leader',
                    'name': leader_data['name'],
                    'department': leader_data['dept'],
                    'leader_quota': quota,
                    'shift': 1
                }
            )
            if created:
                self.stdout.write(f'✓ Created leader: {leader.username}')
            leaders.append(leader)
        
        # 5. Buat foremen untuk setiap leader
        foremen_data = [
            # Foremen untuk Leader 1
            {'username': 'foreman1_1', 'name': 'Foreman 1-1', 'leader_idx': 0, 'dept': 'SUPPORT'},
            {'username': 'foreman1_2', 'name': 'Foreman 1-2', 'leader_idx': 0, 'dept': 'SUPPORT'},
            {'username': 'foreman1_3', 'name': 'Foreman 1-3', 'leader_idx': 0, 'dept': 'SUPPORT'},
            
            # Foremen untuk Leader 2
            {'username': 'foreman2_1', 'name': 'Foreman 2-1', 'leader_idx': 1, 'dept': 'TRACK'},
            {'username': 'foreman2_2', 'name': 'Foreman 2-2', 'leader_idx': 1, 'dept': 'TRACK'},
            
            # Foremen untuk Leader 3
            {'username': 'foreman3_1', 'name': 'Foreman 3-1', 'leader_idx': 2, 'dept': 'PLANT'},
            {'username': 'foreman3_2', 'name': 'Foreman 3-2', 'leader_idx': 2, 'dept': 'PLANT'},
            
            # Foremen untuk Leader 4
            {'username': 'foreman4_1', 'name': 'Foreman 4-1', 'leader_idx': 3, 'dept': 'WHEEL'},
            {'username': 'foreman4_2', 'name': 'Foreman 4-2', 'leader_idx': 3, 'dept': 'WHEEL'},
            {'username': 'foreman4_3', 'name': 'Foreman 4-3', 'leader_idx': 3, 'dept': 'WHEEL'},
        ]
        
        foremen = []
        for foreman_data in foremen_data:
            leader = leaders[foreman_data['leader_idx']]
            foreman, created = User.objects.get_or_create(
                username=foreman_data['username'],
                defaults={
                    'email': f"{foreman_data['username']}@monman.com",
                    'password': make_password('foreman123'),
                    'role': 'foreman',
                    'name': foreman_data['name'],
                    'department': foreman_data['dept'],
                    'leader': leader,
                    'shift': 1,
                    'nrp': f"NRP{foreman_data['username'][-3:]}"
                }
            )
            if created:
                self.stdout.write(f'✓ Created foreman: {foreman.username} under {leader.name}')
                # Update leader quota count
                if leader.leader_quota:
                    leader.leader_quota.current_foreman_count += 1
                    leader.leader_quota.save()
            foremen.append(foreman)
        
        # 6. Buat sample activity reports
        sample_reports = [
            {
                'foreman': foremen[0],  # foreman1_1
                'date': date.today(),
                'shift': 1,
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'activities': 'Maintenance rutin engine PC1250',
                'Unit_Code': 'PC1250-001',
                'Hmkm': '2500',
                'component': 'Component_1',
                'activities_code': 'SC',
                'status': 'pending'
            },
            {
                'foreman': foremen[1],  # foreman1_2
                'date': date.today(),
                'shift': 1,
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'activities': 'Pengecekan hydraulic system',
                'Unit_Code': 'CAT395-002',
                'Hmkm': '1800',
                'component': 'Component_14',
                'activities_code': 'USC',
                'status': 'pending'
            },
            {
                'foreman': foremen[3],  # foreman2_1
                'date': date.today(),
                'shift': 2,
                'start_time': time(16, 0),
                'end_time': time(23, 59),  # Ubah dari time(24, 0) ke time(23, 59)
                'activities': 'Overhaul transmission',
                'Unit_Code': 'D375-003',
                'Hmkm': '3200',
                'component': 'Component_4',
                'activities_code': 'ACD',
                'status': 'approved'
            },
            {
                'foreman': foremen[5],  # foreman3_1
                'date': date.today(),
                'shift': 1,
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'activities': 'Penggantian filter udara',
                'Unit_Code': 'PC500-004',
                'Hmkm': '1500',
                'component': 'Component_1',
                'activities_code': 'SC',
                'status': 'rejected'
            }
        ]
        
        for report_data in sample_reports:
            report, created = ActivityReport.objects.get_or_create(
                foreman=report_data['foreman'],
                date=report_data['date'],
                start_time=report_data['start_time'],
                defaults=report_data
            )
            if created:
                self.stdout.write(f'✓ Created activity report for {report.foreman.name}')
        
        self.stdout.write(self.style.SUCCESS('\n=== DUMMY DATA CREATED SUCCESSFULLY ==='))
        self.stdout.write(f'Superadmin: superadmin / admin123')
        self.stdout.write(f'Admin: admin1 / admin123')
        self.stdout.write(f'Leaders: leader1-4 / leader123')
        self.stdout.write(f'Foremen: foreman1_1, foreman1_2, etc / foreman123')
        self.stdout.write('\nSekarang coba login sebagai leader1 untuk melihat dashboard!')