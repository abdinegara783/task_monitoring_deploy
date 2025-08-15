from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ("leader", "Leader"),
        ("admin", "Admin"),
        ("foreman", "Foreman"),
    ]
    DEPARTMENT_CHOICES = [
        ("SUPPORT", "Support $ Fabrikasi"),
        ("TRACK", "Track"),
        ("PLANT", "Plant Coal Hauling"),
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
    shift = models.IntegerField(default=1, choices=[(1, "Shift 1"), (2, "Shift 2")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ActivityReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    LEADER_CHOICES = [
        ("Leader_1", "YUDI SULISTIYONO"),
        ("Leader_2", "DWI ARI PRASETYA"),
        ("Leader_3", "ADI RIYANTO"),
        ("Leader_4", "MOH FADHOLI"),
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
    leader = models.CharField(
        max_length=100, choices=LEADER_CHOICES, blank=True, null=True
    )
    Unit_Code = models.CharField(max_length=100, blank=True, null=True)
    Hmkm = models.CharField(max_length=100, blank=True, null=True)
    component = models.CharField(
        max_length=100, choices=COMPONENT_CHOICES, blank=True, null=True
    )
    activities_code = models.CharField(
        max_length=100, choices=ACTIVITIES_CHOICES, blank=True, null=True
    )
