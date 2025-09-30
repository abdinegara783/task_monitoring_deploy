from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard.models import LeaderQuota, ActivityReport, AnalysisReport
from datetime import datetime, timedelta, time
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before generating new ones',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Resetting existing data...')
            User.objects.filter(is_superuser=False).delete()
            LeaderQuota.objects.all().delete()
            ActivityReport.objects.all().delete()
            AnalysisReport.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Data reset completed'))

        self.stdout.write('🚀 Generating dummy data...')
        
        # 1. Create Leader Quotas
        self.create_leader_quotas()
        
        # 2. Create Admin Users
        self.create_admin_users()
        
        # 3. Create Leaders
        self.create_leaders()
        
        # 4. Create Foremen
        self.create_foremen()
        
        # 5. Create Reports
        self.create_reports()
        
        self.stdout.write(self.style.SUCCESS('🎉 Dummy data generation completed!'))
        self.print_summary()

    def create_leader_quotas(self):
        """Create leader quotas"""
        self.stdout.write('📊 Creating leader quotas...')
        
        quotas_data = [
            {'name': 'Ahmad Suryanto', 'username': 'ahmad.suryanto', 'max_foreman': 5},
            {'name': 'Budi Hartono', 'username': 'budi.hartono', 'max_foreman': 4},
            {'name': 'Citra Dewi', 'username': 'citra.dewi', 'max_foreman': 6},
            {'name': 'Dedi Kurniawan', 'username': 'dedi.kurniawan', 'max_foreman': 3},
            {'name': 'Eka Pratama', 'username': 'eka.pratama', 'max_foreman': 4},
        ]
        
        for quota_data in quotas_data:
            quota, created = LeaderQuota.objects.get_or_create(
                leader_username=quota_data['username'],
                defaults={
                    'leader_name': quota_data['name'],
                    'max_foreman': quota_data['max_foreman'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created quota: {quota.leader_name} (@{quota.leader_username})')

    def create_admin_users(self):
        """Create admin users"""
        self.stdout.write('👨‍💼 Creating admin users...')
        
        admin_data = [
            {'username': 'admin1', 'name': 'Admin Utama', 'email': 'admin1@company.com', 'role': 'admin'},
            {'username': 'superadmin1', 'name': 'Super Admin', 'email': 'superadmin@company.com', 'role': 'superadmin'},
        ]
        
        for data in admin_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'name': data['name'],
                    'email': data['email'],
                    'role': data['role'],
                    'first_name': data['name'].split()[0],
                    'last_name': ' '.join(data['name'].split()[1:]),
                    'is_staff': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✅ Created {data["role"]}: {user.name} (@{user.username})')

    def create_leaders(self):
        """Create leader users based on quotas"""
        self.stdout.write('👑 Creating leader users...')
        
        departments = ['SUPPORT', 'TRACK', 'PLANT', 'WHEEL']
        
        for quota in LeaderQuota.objects.all():
            if not quota.leader_user:  # Only create if not exists
                user = User.objects.create(
                    username=quota.leader_username,
                    name=quota.leader_name,
                    email=f'{quota.leader_username}@company.com',
                    role='leader',
                    first_name=quota.leader_name.split()[0],
                    last_name=' '.join(quota.leader_name.split()[1:]),
                    department=random.choice(departments),
                    shift=random.choice([1, 2]),
                    nrp=f'L{random.randint(1000, 9999)}',
                    phone=f'08{random.randint(10000000, 99999999)}',
                    is_active=True
                )
                user.set_password('password123')
                user.save()
                
                # Link with quota
                quota.leader_user = user
                quota.save()
                
                self.stdout.write(f'  ✅ Created leader: {user.name} (@{user.username})')

    def create_foremen(self):
        """Create foreman users under leaders"""
        self.stdout.write('🔧 Creating foreman users...')
        
        departments = ['SUPPORT', 'TRACK', 'PLANT', 'WHEEL']
        foreman_names = [
            'Agus Setiawan', 'Bambang Wijaya', 'Cahyo Nugroho', 'Dani Pratama',
            'Eko Susanto', 'Fajar Hidayat', 'Gunawan Saputra', 'Hendra Kurnia',
            'Indra Permana', 'Joko Santoso', 'Krisna Wibowo', 'Lukman Hakim',
            'Maulana Yusuf', 'Nanda Pratama', 'Oscar Ramadhan', 'Putra Mahendra',
            'Qori Abdillah', 'Rizki Firmansyah', 'Sandi Wijaya', 'Taufik Rahman'
        ]
        
        foreman_counter = 0
        
        for leader in User.objects.filter(role='leader'):
            quota = leader.quota_as_leader.first()
            if quota:
                # Create foremen up to quota limit
                foremen_to_create = min(quota.max_foreman, len(foreman_names) - foreman_counter)
                
                for i in range(foremen_to_create):
                    if foreman_counter < len(foreman_names):
                        name = foreman_names[foreman_counter]
                        username = name.lower().replace(' ', '.')
                        
                        # Pastikan username unique
                        counter = 1
                        original_username = username
                        while User.objects.filter(username=username).exists():
                            username = f"{original_username}{counter}"
                            counter += 1
                        
                        foreman = User.objects.create(
                            username=username,
                            name=name,
                            email=f'{username}@company.com',
                            role='foreman',
                            first_name=name.split()[0],
                            last_name=' '.join(name.split()[1:]),
                            leader=leader,
                            department=leader.department,
                            shift=random.choice([1, 2]),
                            nrp=f'F{random.randint(1000, 9999)}',
                            phone=f'08{random.randint(10000000, 99999999)}',
                            is_active=True
                        )
                        foreman.set_password('password123')
                        foreman.save()
                        
                        foreman_counter += 1
                        self.stdout.write(f'  ✅ Created foreman: {foreman.name} (@{foreman.username}) under {leader.name}')
                
                # Update quota count
                quota.update_foreman_count()

    def create_reports(self):
        """Create sample reports"""
        self.stdout.write('📋 Creating sample reports...')
        
        foremen = User.objects.filter(role='foreman')
        
        # Create Activity Reports dengan field yang benar
        for foreman in foremen[:10]:  # Create reports for first 10 foremen
            for i in range(random.randint(2, 5)):
                date = datetime.now().date() - timedelta(days=random.randint(1, 30))
                start_time = datetime.strptime(f'{random.randint(7, 9)}:00', '%H:%M').time()
                end_time = datetime.strptime(f'{random.randint(15, 17)}:00', '%H:%M').time()
                
                ActivityReport.objects.create(
                    foreman=foreman,
                    date=date,
                    shift=foreman.shift,
                    start_time=start_time,
                    end_time=end_time,
                    activities=f'Performed maintenance work on {random.choice(["engine", "hydraulic system", "transmission", "brake system"])}',
                    unit_code=f'HD{random.randint(100, 999)}',
                    Hmkm=f'{random.randint(1000, 5000)}',
                    component=random.choice([
                        'Component_1',  # Engine
                        'Component_14', # Hydraulic
                        'Component_4',  # Transmisi
                        'Component_12', # Brake
                        'Component_26', # Daily Maintenance
                    ]),
                    activities_code=random.choice(['SC', 'USC', 'ACD']),
                    status=random.choice(['pending', 'approved', 'rejected']),
                    feedback=f'Work completed by {foreman.name}' if random.choice([True, False]) else None
                )
        
        # Create Analysis Reports dengan field yang benar
        for foreman in foremen[:5]:  # Create analysis reports for first 5 foremen
            for i in range(random.randint(1, 3)):
                date = datetime.now().date() - timedelta(days=random.randint(1, 15))
                
                AnalysisReport.objects.create(
                    foreman=foreman,
                    report_date=date,
                    no_report=f'TAR/{datetime.now().year}/{random.randint(100, 999)}',
                    unit_code=f'HD{random.randint(100, 999)}',
                    problem=random.choice(['engine_failure', 'hydraulic_leak', 'electrical_issue']),
                    status=random.choice(['pending', 'approved']),
                    WO_Number=f'WO{random.randint(1000, 9999)}',
                    WO_date=date,
                    Trouble_date=date - timedelta(days=1),
                    Hm=f'{random.randint(1000, 5000)}',
                    part_no=f'P{random.randint(1000, 9999)}',
                    part_name=random.choice(['Filter Oil', 'Hydraulic Pump', 'Engine Block', 'Brake Pad'])
                )
        
        self.stdout.write(f'  ✅ Created {ActivityReport.objects.count()} activity reports')
        self.stdout.write(f'  ✅ Created {AnalysisReport.objects.count()} analysis reports')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n📊 SUMMARY:')
        self.stdout.write(f'  👥 Total Users: {User.objects.count()}')
        self.stdout.write(f'  👨‍💼 Admins: {User.objects.filter(role__in=["admin", "superadmin"]).count()}')
        self.stdout.write(f'  👑 Leaders: {User.objects.filter(role="leader").count()}')
        self.stdout.write(f'  🔧 Foremen: {User.objects.filter(role="foreman").count()}')
        self.stdout.write(f'  📊 Leader Quotas: {LeaderQuota.objects.count()}')
        self.stdout.write(f'  📋 Activity Reports: {ActivityReport.objects.count()}')
        self.stdout.write(f'  📈 Analysis Reports: {AnalysisReport.objects.count()}')
        
        self.stdout.write('\n🔑 LOGIN CREDENTIALS:')
        self.stdout.write('  All users have password: password123')
        self.stdout.write('  Superadmin: superadmin1 / password123')
        self.stdout.write('  Admin: admin1 / password123')
        
        self.stdout.write('\n🎯 LEADER QUOTAS:')
        for quota in LeaderQuota.objects.all():
            status = '✅ User Created' if quota.leader_user else '❌ No User'
            self.stdout.write(f'  {quota.leader_name} (@{quota.leader_username}): {quota.current_foreman_count}/{quota.max_foreman} - {status}')