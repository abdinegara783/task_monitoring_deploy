from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta


class LeaderQuota(models.Model):
    leader_name = models.CharField(max_length=100)
    leader_username = models.CharField(max_length=150, unique=True)  # Tambah field username
    leader_user = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'leader'},
        related_name='quota_as_leader'  # Ubah related_name untuk menghindari konflik
    )
    max_foreman = models.PositiveIntegerField(default=0)
    current_foreman_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.leader_name} (@{self.leader_username}) - {self.current_foreman_count}/{self.max_foreman}"

    def can_add_foreman(self):
        return self.current_foreman_count < self.max_foreman and self.is_active
    
    @property
    def available_slots(self):
        return max(0, self.max_foreman - self.current_foreman_count)
    
    def update_foreman_count(self):
        if self.leader_user:
            actual_count = User.objects.filter(
                leader=self.leader_user, 
                role='foreman', 
                is_active=True
            ).count()
            self.current_foreman_count = actual_count
            self.save()
        return self.current_foreman_count
    
    @classmethod
    def is_username_registered(cls, username):
        """Cek apakah username terdaftar di kuota leader"""
        return cls.objects.filter(leader_username=username, is_active=True).exists()
    
    @classmethod
    def get_quota_by_username(cls, username):
        """Ambil kuota berdasarkan username"""
        try:
            return cls.objects.get(leader_username=username, is_active=True)
        except cls.DoesNotExist:
            return None

    class Meta:
        verbose_name = "Leader Quota"
        verbose_name_plural = "Leader Quotas"


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("superadmin", "Super Admin"),
        ("leader", "Leader"),
        ("foreman", "Foreman"),
    ]

    DEPARTMENT_CHOICES = [
        ("SUPPORT", "Support & Fabrikasi"),
        ("TRACK", "Track"),
        ("PLANT", "PCH"),
        ("WHEEL", "Wheel"),
    ]

    name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    nrp = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Telegram Chat ID untuk notifikasi")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="foreman")
    department = models.CharField(
        max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True
    )

    # Relasi untuk hierarki leader-foreman
    leader = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "leader"},
        related_name="foremen",
    )

    shift = models.IntegerField(default=1, choices=[(1, "Shift 1"), (2, "Shift 2")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-update foreman count ketika foreman disimpan
        if self.role == "foreman" and self.leader:
            # Gunakan reverse relation yang baru: quota_as_leader
            quota = self.leader.quota_as_leader.first()
            if quota:
                # Jika ini adalah foreman baru
                if not self.pk:
                    quota.current_foreman_count += 1
                    quota.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update foreman count ketika foreman dihapus
        if self.role == "foreman" and self.leader:
            quota = self.leader.quota_as_leader.first()
            if quota:
                quota.current_foreman_count = max(0, quota.current_foreman_count - 1)
                quota.save()
        
        super().delete(*args, **kwargs)

    def get_full_name(self):
        if self.name:
            return self.name
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class ActivityReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    SECTION_CHOICES = [
        ("PC1250", "PC1250"),
        ("CAT395", "CAT395"),
        ("DX800", "DX800"),
        ("PC500", "PC500"),
        ("PC300", "PC300"),
        ("PC200/210", "PC200/210"),
        ("D375", "D375"),
        ("D155", "D155"),
        ("D85", "D85"),
        ("EPIROC DM30", "EPIROC DM30"),
        ("HD785", "HD785"),
        ("VOLVO FMX400", "VOLVO FMX400"),
        ("GD955", "GD955"),
        ("GD535", "GD535"),
        ("GD160K/M", "GD160K/M"),
        ("DYNAPAC COMPACTOR", "DYNAPAC COMPACTOR"),
        ("HD465/WT", "HD465/WT"),
        ("RENAULT FT/LB", "RENAULT FT/LB"),
        ("HINO WT/LT/CT", "HINO WT/LT/CT"),
        ("MANITAOU", "MANITAOU"),
        ("KATO CRANE", "KATO CRANE"),
        ("GENSET", "GENSET"),
        ("WATER PUMP (WP)", "WATER PUMP (WP)"),
        ("HINO DT", "HINO DT"),
        ("MERCY DT", "MERCY DT"),
        ("BOMAG COMPACTOR", "BOMAG COMPACTOR"),
        ("TL", "TL")
    ]

    COMPONENT_CHOICES = [
        ("Component_1", "Engine"),
        ("Component_2", "Clutch - Couper"),
        ("Component_3", "PTO"),
        ("Component_4", "Transmisi"),
        ("Component_5", "Final Drive"),
        ("Component_6", "Travel - Axle"),
        ("Component_7", "Steering"),
        ("Component_8", "Under Carriage"),
        ("Component_9", "Wheel"),
        ("Component_10", "Frame & Guard"),
        ("Component_11", "Electric"),
        ("Component_12", "Brake"),
        ("Component_13", "Suspension"),
        ("Component_14", "Hydraulic"),
        ("Component_15", "Pneumatic"),
        ("Component_16", "Swing System"),
        ("Component_17", "Attachment"),
        ("Component_18", "GET"),
        ("Component_19", "Vessel Assy"),
        ("Component_20", "Generating Set"),
        ("Component_21", "Dewatering Pump"),
        ("Component_22", "Optional Accessories"),
        ("Component_23", "Tank & Piping"),
        ("Component_24", "AC"),
        ("Component_25", "Stone Crusher"),
        ("Component_26", "Daily Maintenance"),
        ("Component_27", "12 Mounth Service"),
        ("Component_28", "6 Mounth Service"),
        ("Component_29", "90 Days Service"),
        ("Component_30", "30 Days Service"),
        ("Component_31", "10 Dayts Service"),
        ("Component_32", "PPA"),
        ("Component_33", "PPU"),
        ("Component_34", "PPM"),
        ("Component_35", "PAP"),
        ("Component_36", "4000 Hour Service"),
        ("Component_37", "2000 Hour Service"),
        ("Component_38", "1000 Hour Service"),
        ("Component_39", "500 Hour Service"),
        ("Component_40", "250 Hour Service"),
        ("Component_41", "100 Hour Service (Inisial)"),
        ("Component_42", "50 Hour Service (inisial)"),
        ("Component_43", "100 Hour Dialy Check"),
        ("Component_44", "Component Overhaul"),
        ("Component_45", "Component Midlive"),
        ("Component_46", "20.000 KM Service"),
        ("Component_47", "15.000 KM Service"),
        ("Component_48", "10.000 KM Service"),
        ("Component_49", "5.000 KM Service"),
        ("Component_50", "2.500 KM Service"),
    ]
    
    ACTIVITIES_CHOICES = [
        ("SC", "SC"),
        ("USC", "USC"),
        ("ACD", "ACD"),
    ]

    # Main report information
    foreman = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "foreman"}
    )
    nrp = models.CharField(max_length=20, help_text="Nomor Registrasi Pegawai")
    section = models.CharField(
        max_length=100, choices=SECTION_CHOICES, help_text="Section/Track"
    )
    date = models.DateField(help_text="Tanggal laporan")
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Activity Report - {self.foreman.get_full_name()} - {self.date}"

    class Meta:
        verbose_name = "Activity Report"
        verbose_name_plural = "Activity Reports"
        ordering = ['-date', '-created_at']


class ActivityReportDetail(models.Model):
    """Detail aktivitas untuk setiap activity report (maksimal 5 aktivitas)"""
    
    activity_report = models.ForeignKey(
        ActivityReport, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    activity_number = models.PositiveIntegerField(
        help_text="Nomor urut aktivitas (1-5)"
    )
    
    # Activity details
    unit_code = models.CharField(
        max_length=100, 
        help_text="Unit Code untuk aktivitas ini"
    )
    hm_km = models.CharField(
        max_length=100, 
        help_text="HM/KM untuk aktivitas ini"
    )
    start_time = models.TimeField(help_text="Waktu mulai aktivitas")
    stop_time = models.TimeField(help_text="Waktu selesai aktivitas")
    component = models.CharField(
        max_length=100, 
        choices=ActivityReport.COMPONENT_CHOICES,
        help_text="Komponen yang dikerjakan"
    )
    activities = models.TextField(help_text="Deskripsi aktivitas yang dilakukan")
    activity_code = models.CharField(
        max_length=10, 
        choices=ActivityReport.ACTIVITIES_CHOICES,
        help_text="Kode aktivitas (SC/USC/ACD)"
    )

    def __str__(self):
        return f"Activity {self.activity_number} - {self.activity_report}"

    class Meta:
        verbose_name = "Activity Report Detail"
        verbose_name_plural = "Activity Report Details"
        ordering = ['activity_report', 'activity_number']
        unique_together = ['activity_report', 'activity_number']


class AnalysisReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    SECTION_CHOICES = [
        # Equipment yang sudah ada
        ("PC1250", "PC1250"),
        ("CAT395", "CAT395"),
        ("DX800", "DX800"),
        ("PC500", "PC500"),
        ("PC300", "PC300"),
        ("PC200/210", "PC200/210"),
        ("D375", "D375"),
        ("D155", "D155"),
        ("D85", "D85"),
        ("EPIROC DM30", "EPIROC DM30"),
        # Equipment baru yang ditambahkan
        ("HD785", "HD785"),
        ("VOLVO FMX400", "VOLVO FMX400"),
        ("GD955", "GD955"),
        ("GD535", "GD535"),
        ("GD160K/M", "GD160K/M"),
        ("DYNAPAC COMPACTOR", "DYNAPAC COMPACTOR"),
        ("HD465/WT", "HD465/WT"),
        ("RENAULT FT/LB", "RENAULT FT/LB"),
        ("HINO WT/LT/CT", "HINO WT/LT/CT"),
        ("MANITAOU", "MANITAOU"),
        ("KATO CRANE", "KATO CRANE"),
        ("GENSET", "GENSET"),
        ("WATER PUMP (WP)", "WATER PUMP (WP)"),
        ("HINO DT", "HINO DT"),
        ("MERCY DT", "MERCY DT"),
        ("BOMAG COMPACTOR", "BOMAG COMPACTOR"),
        ("TL","TL")
    ]
    PROBLEM_CHOICES = [
        ("1000", "Engine"),
        ("2000", "Clutch System"),
        ("3000", "Transmission"),
        ("4000", "Travel Dive-Axle"),
        ("5000", "Steering"),
        ("6000", "Undercariage"),
        ("7000", "Electric"),
        ("8000", "Attachment"),
        ("9000", "Periodical Services"),
    ]
    
    # Choices untuk faktor 4M1E
    FACTOR_4M1E_CHOICES = [
        ("man", "Man (Manusia)"),
        ("material", "Material"),
        ("machine", "Machine (Mesin)"),
        ("method", "Method (Metode)"),
        ("environment", "Environment (Lingkungan)"),
    ]

    # Field yang sudah ada
    foreman = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "foreman"}
    )
    section_track = models.CharField(
        max_length=100, choices=SECTION_CHOICES, blank=True, null=True
    )
    email = models.EmailField(max_length=100, blank=True, null=True)
    no_report = models.CharField(max_length=100, blank=True, null=True)
    report_date = models.DateField()
    WO_Number = models.CharField(max_length=100, blank=True, null=True)
    WO_date = models.DateField()
    unit_code = models.CharField(max_length=100, blank=True, null=True)
    problem = models.CharField(
        max_length=100, choices=PROBLEM_CHOICES, blank=True, null=True
    )
    Trouble_date = models.DateField()
    Hm = models.CharField(max_length=100, blank=True, null=True)
    title_problem = models.TextField()
    part_no = models.CharField(max_length=100, blank=True, null=True)
    part_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    # Field baru yang ditambahkan
    nama_fungsi_komponen = models.TextField(
        verbose_name="Nama & Fungsi Komponen",
        help_text="Jelaskan nama dan fungsi komponen yang bermasalah",
        blank=True, null=True
    )
    
    gejala_masalah = models.TextField(
        verbose_name="Gejala Masalah yang Dihadapi",
        help_text="Deskripsikan gejala masalah yang dihadapi",
        blank=True, null=True
    )
    
    akar_penyebab_masalah = models.TextField(
        verbose_name="Akar Penyebab Masalah",
        help_text="Jelaskan akar penyebab masalah berdasarkan analisis",
        blank=True, null=True
    )
    
    # Faktor 4M1E - Text input untuk penjelasan spesifik
    faktor_man = models.TextField(
        verbose_name="Man (Manusia)",
        help_text="Jelaskan faktor manusia yang berkontribusi terhadap masalah (contoh: Terjadi kelalaian pada saat monitoring)",
        blank=True, null=True
    )
    faktor_material = models.TextField(
        verbose_name="Material",
        help_text="Jelaskan faktor material yang berkontribusi terhadap masalah",
        blank=True, null=True
    )
    faktor_machine = models.TextField(
        verbose_name="Machine (Mesin)",
        help_text="Jelaskan faktor mesin yang berkontribusi terhadap masalah",
        blank=True, null=True
    )
    faktor_method = models.TextField(
        verbose_name="Method (Metode)",
        help_text="Jelaskan faktor metode yang berkontribusi terhadap masalah",
        blank=True, null=True
    )
    faktor_environment = models.TextField(
        verbose_name="Environment (Lingkungan)",
        help_text="Jelaskan faktor lingkungan yang berkontribusi terhadap masalah",
        blank=True, null=True
    )
    
    tindakan_dilakukan = models.TextField(
        verbose_name="Tindakan yang Dilakukan",
        help_text="Jelaskan tindakan yang telah dilakukan untuk mengatasi masalah",
        blank=True, null=True
    )
    
    tindakan_pencegahan = models.TextField(
        verbose_name="Tindakan Pencegahan",
        help_text="Jelaskan tindakan pencegahan untuk mencegah masalah serupa",
        blank=True, null=True
    )
    
    # File upload untuk dokumentasi
    dokumentasi_sebelum = models.FileField(
        upload_to='analysis_reports/before/',
        verbose_name="Dokumentasi Sebelum",
        help_text="Upload gambar/drawing sebelum perbaikan (Max 1MB)",
        blank=True, null=True
    )
    
    dokumentasi_sesudah = models.FileField(
        upload_to='analysis_reports/after/',
        verbose_name="Dokumentasi Sesudah",
        help_text="Upload gambar/drawing sesudah perbaikan (Max 1MB)",
        blank=True, null=True
    )
    
    def get_faktor_4m1e_list(self):
        """Return list of selected 4M1E factors"""
        factors = []
        if self.faktor_man:
            factors.append("Man (Manusia)")
        if self.faktor_material:
            factors.append("Material")
        if self.faktor_machine:
            factors.append("Machine (Mesin)")
        if self.faktor_method:
            factors.append("Method (Metode)")
        if self.faktor_environment:
            factors.append("Environment (Lingkungan)")
        return factors
    
    def __str__(self):
        return f"Analysis Report - {self.foreman.name} - {self.report_date}"
    
    class Meta:
        verbose_name = "Analysis Report"
        verbose_name_plural = "Analysis Reports"
        ordering = ['-created_at']


class Notification(models.Model):
    """Model sederhana untuk sistem notifikasi broadcast"""
    
    STATUS_CHOICES = [
        ('unread', 'Belum Dibaca'),
        ('read', 'Sudah Dibaca'),
    ]
    
    # Target penerima notifikasi
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="Penerima notifikasi"
    )
    
    # Deskripsi konten notifikasi
    title = models.CharField(max_length=200, help_text="Judul notifikasi")
    message = models.TextField(help_text="Isi pesan notifikasi")
    
    # Status baca/belum baca
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='unread',
        help_text="Status baca notifikasi"
    )
    
    # Waktu pengiriman notifikasi
    created_at = models.DateTimeField(auto_now_add=True, help_text="Waktu notifikasi dibuat")
    read_at = models.DateTimeField(null=True, blank=True, help_text="Waktu notifikasi dibaca")
    
    # Pengirim notifikasi (superuser)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        help_text="Admin yang mengirim notifikasi"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notifikasi"
        verbose_name_plural = "Notifikasi"
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.name} ({self.status})"
    
    def mark_as_read(self):
        """Tandai notifikasi sebagai sudah dibaca"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_broadcast_notification(cls, title, message, recipients, created_by):
        """Buat notifikasi broadcast untuk multiple recipients"""
        notifications = []
        for recipient in recipients:
            notification = cls.objects.create(
                recipient=recipient,
                title=title,
                message=message,
                created_by=created_by
            )
            notifications.append(notification)
        return notifications
