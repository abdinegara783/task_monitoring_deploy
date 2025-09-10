from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta


class LeaderQuota(models.Model):
    leader_name = models.CharField(max_length=100, unique=True)
    max_foreman = models.PositiveIntegerField(default=0)
    current_foreman_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.leader_name} ({self.current_foreman_count}/{self.max_foreman})"

    def can_add_foreman(self):
        return self.current_foreman_count < self.max_foreman and self.is_active

    class Meta:
        verbose_name = "Leader Quota"
        verbose_name_plural = "Leader Quotas"


class User(AbstractUser):
    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Admin"),
        ("leader", "Leader"),
        ("foreman", "Mekanik"),  # Ubah dari "Foreman" menjadi "Mekanik"
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

    # Relasi ke LeaderQuota untuk leader
    leader_quota = models.OneToOneField(
        LeaderQuota,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leader_user",
    )

    shift = models.IntegerField(default=1, choices=[(1, "Shift 1"), (2, "Shift 2")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-update foreman count ketika foreman disimpan
        if self.role == "foreman" and self.leader:
            if self.leader.leader_quota:
                # Jika ini adalah foreman baru
                if not self.pk:
                    self.leader.leader_quota.current_foreman_count += 1
                    self.leader.leader_quota.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update foreman count ketika foreman dihapus
        if self.role == "foreman" and self.leader and self.leader.leader_quota:
            self.leader.leader_quota.current_foreman_count -= 1
            self.leader.leader_quota.save()

        super().delete(*args, **kwargs)


class ActivityReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
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
    foreman = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "foreman"}
    )
    date = models.DateField()
    shift = models.IntegerField(choices=[(1, "Shift 1"), (2, "Shift 2")], default=1)
    start_time = models.TimeField()
    end_time = models.TimeField()
    activities = models.TextField()
    Unit_Code = models.CharField(max_length=100, blank=True, null=True)
    Hmkm = models.CharField(max_length=100, blank=True, null=True)
    component = models.CharField(
        max_length=100, choices=COMPONENT_CHOICES, blank=True, null=True
    )
    activities_code = models.CharField(
        max_length=100, choices=ACTIVITIES_CHOICES, blank=True, null=True
    )

    # Tambahkan field status dan feedback
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


# Tambahkan field baru di AnalysisReport class (setelah line 230)

class AnalysisReport(models.Model):
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
    
    # Faktor 4M1E - Multiple choice dengan checkbox
    faktor_man = models.BooleanField(
        default=False,
        verbose_name="Man (Manusia)",
        help_text="Faktor manusia sebagai penyebab masalah"
    )
    faktor_material = models.BooleanField(
        default=False,
        verbose_name="Material",
        help_text="Faktor material sebagai penyebab masalah"
    )
    faktor_machine = models.BooleanField(
        default=False,
        verbose_name="Machine (Mesin)",
        help_text="Faktor mesin sebagai penyebab masalah"
    )
    faktor_method = models.BooleanField(
        default=False,
        verbose_name="Method (Metode)",
        help_text="Faktor metode sebagai penyebab masalah"
    )
    faktor_environment = models.BooleanField(
        default=False,
        verbose_name="Environment (Lingkungan)",
        help_text="Faktor lingkungan sebagai penyebab masalah"
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
    NOTIFICATION_TYPES = [
        ("activity_reminder", "Activity Report Reminder"),
        ("analysis_reminder", "Analysis Report Reminder"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Auto-remove when task is completed
    auto_remove_on_completion = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["notification_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    @classmethod
    def create_activity_reminder(cls, user, hours_left):
        """Create activity report reminder"""
        if hours_left == 1:
            title = "⏰ Deadline Activity Report - 1 Jam Lagi!"
            message = "Jangan lupa isi activity report hari ini. Deadline dalam 1 jam lagi (18:00)."
        elif hours_left == 0.5:  # 30 minutes
            title = "🚨 Deadline Activity Report - 30 Menit Lagi!"
            message = "Segera isi activity report hari ini! Deadline dalam 30 menit lagi (18:00)."
        elif hours_left == 1 / 6:  # 10 minutes
            title = "🔥 URGENT: Activity Report - 10 Menit Lagi!"
            message = "URGENT! Activity report harus diisi sekarang! Deadline dalam 10 menit lagi (18:00)."
        else:
            return None

        # Check if similar notification already exists today
        today = timezone.now().date()
        existing = cls.objects.filter(
            user=user,
            notification_type="activity_reminder",
            created_at__date=today,
            title=title,
        ).exists()

        if not existing:
            return cls.objects.create(
                user=user,
                notification_type="activity_reminder",
                title=title,
                message=message,
            )
        return None

    @classmethod
    def create_analysis_reminder(cls, user, days_left, missing_count):
        """Create analysis report reminder"""
        if days_left == 3:
            title = f"📊 Analysis Report Reminder - {missing_count} Laporan Kurang"
            message = f"Anda masih kekurangan {missing_count} analysis report bulan ini. Deadline dalam 3 hari lagi."
        else:
            return None

        # Check if similar notification already exists this month
        today = timezone.now().date()
        existing = cls.objects.filter(
            user=user,
            notification_type="analysis_reminder",
            created_at__month=today.month,
            created_at__year=today.year,
        ).exists()

        if not existing:
            return cls.objects.create(
                user=user,
                notification_type="analysis_reminder",
                title=title,
                message=message,
            )
        return None

    @classmethod
    def remove_completed_notifications(cls, user, notification_type):
        """Remove notifications when task is completed"""
        cls.objects.filter(
            user=user,
            notification_type=notification_type,
            auto_remove_on_completion=True,
        ).delete()
