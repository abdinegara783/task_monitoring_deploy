from typing import Required
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets
from .models import User as CustomUser
from .models import User, ActivityReport, AnalysisReport, LeaderQuota, ActivityReportDetail
from django.utils import timezone


class LeaderQuotaForm(forms.ModelForm):
    class Meta:
        model = LeaderQuota
        fields = ["leader_name", "max_foreman"]
        widgets = {
            "leader_name": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Nama lengkap leader",
                }
            ),
            "leader_username": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Username yang akan digunakan leader",
                }
            ),
            "max_foreman": forms.NumberInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Maksimal jumlah mekanik",
                    "min": "1",
                }
            ),
        }
        labels = {
            "leader_name": "Nama Leader",
            "leader_username": "Username Leader",
            "max_foreman": "Maksimal Mekanik",
        }

    def clean_leader_username(self):
        username = self.cleaned_data.get("leader_username")
        if username:
            # Check if username already exists in User model
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    "Username ini sudah digunakan oleh user lain."
                )

            # Check if username already exists in other LeaderQuota instances
            if self.instance.pk:
                existing = LeaderQuota.objects.filter(leader_username=username).exclude(
                    pk=self.instance.pk
                )
            else:
                existing = LeaderQuota.objects.filter(leader_username=username)

            if existing.exists():
                raise forms.ValidationError(
                    "Username ini sudah terdaftar di kuota leader lain."
                )

        return username


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "h-11 flex w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
                "placeholder": "nama@company.com",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "h-11 flex w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm pr-10",
                "placeholder": "Masukkan password",
            }
        )
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control",
            }
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nama Depan",
                "class": "form-control",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nama Belakang",
                "class": "form-control",
            }
        ),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
            }
        ),
    )
    password2 = forms.CharField(
        label="Konfirmasi Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Konfirmasi Password",
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class EmployeeRegistrationForm(forms.ModelForm):
    # Password fields (optional for editing)
    password1 = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                "placeholder": "Kosongkan jika tidak ingin mengubah password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Konfirmasi Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                "placeholder": "Konfirmasi password baru",
            }
        ),
    )

    # Leader field with dynamic queryset
    leader = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Will be set in __init__
        required=False,
        empty_label="Pilih Leader",
        widget=forms.Select(
            attrs={
                "class": "leader-select block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                "id": "id_leader",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "name",
            "phone",
            "nrp",
            "role",
            "department",
            "leader",
            "shift",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Username karyawan",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "email@company.com",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Nama depan",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Nama belakang",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Nama lengkap",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "08123456789",
                }
            ),
            "nrp": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Nomor Registrasi Pegawai",
                }
            ),
            "role": forms.Select(  # Perbaiki dari " f" ke "role"
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400"
                }
            ),
            "department": forms.Select(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Departemen",
                }
            ),
            "shift": forms.Select(
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for leader field to only include users with 'leader' role
        self.fields["leader"].queryset = User.objects.filter(role="leader")

        # If editing existing user, make username readonly
        if self.instance.pk:
            self.fields["username"].widget.attrs["readonly"] = True

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Only validate passwords if they are provided
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Password dan konfirmasi password tidak cocok.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        # Only set password if provided
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user


class ActivityReportDetailForm(forms.ModelForm):
    class Meta:
        model = ActivityReportDetail
        fields = [
            "unit_code",
            "hm_km",
            "start_time",
            "stop_time",
            "component",
            "activities",
            "activity_code",
        ]
        widgets = {
            "unit_code": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Unit Code",
                }
            ),
            "hm_km": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "HM/KM",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "stop_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "component": forms.Select(
                attrs={
                    "class": "select-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "activities": forms.Textarea(
                attrs={
                    "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "rows": 3,
                    "placeholder": "Deskripsi aktivitas yang dilakukan",
                }
            ),
            "activity_code": forms.Select(
                attrs={
                    "class": "select-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
        }


# Create the formset
ActivityReportDetailFormSet = forms.inlineformset_factory(
    ActivityReport,
    ActivityReportDetail,
    form=ActivityReportDetailForm,
    extra=1,  # Start with 1 empty form
    max_num=5,  # Maximum 5 activities
    min_num=1,  # Minimum 1 activity required
    validate_min=True,
    validate_max=True,
    can_delete=True
)


# Initial form untuk Data Dasar laporan (Step 1)
class ActivityReportInitialForm(forms.Form):
    nrp = forms.CharField(
        label="NRP",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                "placeholder": "NRP",
            }
        ),
    )
    section = forms.ChoiceField(
        label="Section",
        choices=ActivityReport.SECTION_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "select-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
            }
        ),
    )
    date = forms.DateField(
        label="Tanggal",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Set default date ke hari ini
        self.fields["date"].initial = timezone.now().date()
        # Prefill NRP dari user jika ada
        if user and getattr(user, "nrp", None):
            self.fields["nrp"].initial = user.nrp
        # Buat NRP tidak bisa diedit di form
        self.fields["nrp"].disabled = True
        self.fields["nrp"].widget.attrs.update({
            "readonly": True,
            "class": "input-field block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-700 cursor-not-allowed",
        })


# Form untuk step 1 analysis report
class AnalysisReportForm(forms.ModelForm):
    """Form untuk step 1 analysis report"""

    class Meta:
        model = AnalysisReport
        fields = [
            "section_track",
            "email",
            "no_report",
            "report_date",
            "WO_Number",
            "WO_date",
            "unit_code",
            "problem",
            "Trouble_date",
            "Hm",
            "title_problem",
            "part_no",
            "part_name",
        ]
        widgets = {
            "report_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "WO_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "Trouble_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "title_problem": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "section_track": forms.Select(attrs={"class": "form-control"}),
            "problem": forms.Select(attrs={"class": "form-control"}),
            "no_report": forms.TextInput(attrs={"class": "form-control"}),
            "WO_Number": forms.TextInput(attrs={"class": "form-control"}),
            "unit_code": forms.TextInput(attrs={"class": "form-control"}),
            "Hm": forms.TextInput(attrs={"class": "form-control"}),
            "part_no": forms.TextInput(attrs={"class": "form-control"}),
            "part_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["report_date"].initial = timezone.now().date()
        self.fields["Trouble_date"].initial = timezone.now().date()
        if user:
            self.fields["email"].initial = user.email


class AnalysisReportExtendedForm(forms.ModelForm):
    """Form untuk field tambahan analysis report - step 2"""
    
    # Custom fields untuk upload gambar
    dokumentasi_sebelum = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200", 
                "accept": "image/*"
            }
        ),
        label="Dokumentasi Sebelum (Max 1MB)"
    )
    
    dokumentasi_sesudah = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200", 
                "accept": "image/*"
            }
        ),
        label="Dokumentasi Sesudah (Max 1MB)"
    )

    class Meta:
        model = AnalysisReport
        fields = [
            "nama_fungsi_komponen",
            "gejala_masalah",
            "akar_penyebab_masalah",
            "faktor_man",
            "faktor_material",
            "faktor_machine",
            "faktor_method",
            "faktor_environment",
            "tindakan_dilakukan",
            "tindakan_pencegahan",
        ]
        widgets = {
            "nama_fungsi_komponen": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Jelaskan nama dan fungsi komponen yang bermasalah...",
                }
            ),
            "gejala_masalah": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Deskripsikan gejala masalah yang dihadapi...",
                }
            ),
            "akar_penyebab_masalah": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Jelaskan akar penyebab masalah berdasarkan analisis...",
                }
            ),
            "tindakan_dilakukan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Jelaskan tindakan yang telah dilakukan untuk mengatasi masalah...",
                }
            ),
            "tindakan_pencegahan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Jelaskan tindakan pencegahan untuk mencegah masalah serupa...",
                }
            ),
            # Textarea styling untuk faktor 4M1E
            "faktor_man": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Contoh: Kelalaian para pekerja dalam melakukan monitoring...",
                }
            ),
            "faktor_material": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Contoh: Material yang digunakan tidak sesuai spesifikasi...",
                }
            ),
            "faktor_machine": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Contoh: Mesin mengalami kerusakan pada komponen utama...",
                }
            ),
            "faktor_method": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Contoh: Prosedur kerja yang tidak sesuai SOP...",
                }
            ),
            "faktor_environment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Contoh: Kondisi cuaca yang ekstrem mempengaruhi kinerja...",
                }
            ),
        }
        labels = {
            "nama_fungsi_komponen": "Nama & Fungsi Komponen",
            "gejala_masalah": "Gejala Masalah yang Dihadapi",
            "akar_penyebab_masalah": "Akar Penyebab Masalah",
            "faktor_man": "Man (Manusia)",
            "faktor_material": "Material",
            "faktor_machine": "Machine (Mesin)",
            "faktor_method": "Method (Metode)",
            "faktor_environment": "Environment (Lingkungan)",
            "tindakan_dilakukan": "Tindakan yang Dilakukan",
            "tindakan_pencegahan": "Tindakan Pencegahan",
        }
    
    def clean_dokumentasi_sebelum(self):
        image = self.cleaned_data.get('dokumentasi_sebelum')
        if image:
            if image.size > 1024 * 1024:  # 1MB
                raise forms.ValidationError("Ukuran file tidak boleh lebih dari 1MB")
        return image
    
    def clean_dokumentasi_sesudah(self):
        image = self.cleaned_data.get('dokumentasi_sesudah')
        if image:
            if image.size > 1024 * 1024:  # 1MB
                raise forms.ValidationError("Ukuran file tidak boleh lebih dari 1MB")
        return image
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle image uploads
        dokumentasi_sebelum = self.cleaned_data.get('dokumentasi_sebelum')
        dokumentasi_sesudah = self.cleaned_data.get('dokumentasi_sesudah')
        
        if dokumentasi_sebelum:
            instance.save_image_to_database(dokumentasi_sebelum, 'sebelum')
        
        if dokumentasi_sesudah:
            instance.save_image_to_database(dokumentasi_sesudah, 'sesudah')
        
        if commit:
            instance.save()
        
        return instance


class RoleBasedUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm",
                "placeholder": "Masukkan password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Konfirmasi Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm",
                "placeholder": "Konfirmasi password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "name",
            "phone",
            "nrp",
            "role",
            "department",
            "shift",
            "leader",
        ]
        widgets = {
            "role": forms.Select(
                attrs={"class": "select-field", "onchange": "toggleLeaderField()"}
            ),
            "leader": forms.Select(
                attrs={"class": "select-field", "id": "leader-field"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for leader field
        self.fields["leader"].queryset = User.objects.filter(role="leader")

        # Make leader field conditional based on role
        if "role" in self.data:
            role = self.data.get("role")
            if role != "foreman":
                self.fields["leader"].required = False
                self.fields["leader"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Password dan konfirmasi password tidak cocok.")

        # Validate leader field for foreman role
        role = cleaned_data.get("role")
        leader = cleaned_data.get("leader")

        if role == "foreman" and not leader:
            raise forms.ValidationError({"leader": "Leader harus dipilih untuk role foreman."})

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user


class LeaderQuotaForm(forms.ModelForm):
    class Meta:
        model = LeaderQuota
        fields = ["leader_name", "leader_username", "max_foreman", "is_active"]
        widgets = {
            "leader_name": forms.TextInput(
                attrs={"class": "input-field", "readonly": True}
            ),
            "leader_username": forms.TextInput(
                attrs={"class": "input-field", "readonly": True}
            ),
            "max_foreman": forms.NumberInput(
                attrs={"class": "input-field", "min": "0"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox-field"}),
        }
