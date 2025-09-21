# Remove unused 'email' import
from typing import Required
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets
from .models import User as CustomUser
from .models import User, ActivityReport, AnalysisReport, LeaderQuota
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
            # Cek apakah username sudah digunakan di User
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    "Username ini sudah digunakan oleh user lain."
                )

            # Cek apakah username sudah ada di kuota lain (untuk edit)
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


# NEW: Form untuk Admin menambah karyawan
class EmployeeRegistrationForm(forms.ModelForm):
    """Form untuk admin mendaftarkan karyawan baru"""

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

    # Custom field untuk leader dengan informasi kuota
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
            "department": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                    "placeholder": "Departemen/Divisi",
                }
            ),
            "shift": forms.Select(
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400"
                }
            ),
        }
        labels = {
            "username": "Username",
            "email": "Email",
            "first_name": "Nama Depan",
            "last_name": "Nama Belakang",
            "name": "Nama Lengkap",
            "phone": "Nomor Telepon",
            "nrp": "NRP",
            "role": "Role/Jabatan",
            "department": "Departemen",
            "shift": "Shift Kerja",
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 or password2:
            if not password1:
                raise forms.ValidationError(
                    "Password harus diisi jika ingin mengubah password"
                )
            if not password2:
                raise forms.ValidationError("Konfirmasi password harus diisi")
            if password1 != password2:
                raise forms.ValidationError("Password tidak cocok")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)

        # Hanya update password jika diisi
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)

        if commit:
            user.save()
        return user


class ActivityReportForm(forms.ModelForm):
    class Meta:
        model = ActivityReport
        fields = [
            "date",
            "shift",  # Tambahkan shift yang hilang
            "Unit_Code",
            "Hmkm",
            "start_time",
            "end_time",
            "component",
            "activities",
            "activities_code",
        ]  # Hapus "foreman" dari fields
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "shift": forms.Select(
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "Unit_Code": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Masukkan kode unit",
                }
            ),
            "Hmkm": forms.TextInput(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "placeholder": "Masukkan HM/KM",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "component": forms.Select(
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "activities": forms.Textarea(
                attrs={
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                    "rows": 4,
                    "placeholder": "Deskripsikan aktivitas yang dilakukan",
                }
            ),
            "activities_code": forms.Select(
                attrs={
                    "class": "select-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
        }
        labels = {
            "date": "Tanggal",
            "shift": "Shift",
            "Unit_Code": "Unit Code",
            "Hmkm": "HM/KM",
            "start_time": "Waktu Mulai",
            "end_time": "Waktu Selesai",
            "component": "Component",
            "activities": "Activity",
            "activities_code": "Activity Code",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:  # Only for new instances
            self.fields["date"].initial = timezone.now().date()
            self.fields["shift"].initial = 1


# Tambahkan di akhir forms.py


class AnalysisReportForm(forms.ModelForm):
    """Form untuk analysis report - step 1 (basic info)"""

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
        # Set default values
        self.fields["report_date"].initial = timezone.now().date()
        self.fields["WO_date"].initial = timezone.now().date()
        self.fields["Trouble_date"].initial = timezone.now().date()
        if user:
            self.fields["email"].initial = user.email


class AnalysisReportExtendedForm(forms.ModelForm):
    """Form untuk field tambahan analysis report - step 2"""

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
            "dokumentasi_sebelum",
            "dokumentasi_sesudah",
        ]
        widgets = {
            "nama_fungsi_komponen": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Jelaskan nama dan fungsi komponen yang bermasalah...",
                }
            ),
            "gejala_masalah": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Deskripsikan gejala masalah yang dihadapi...",
                }
            ),
            "akar_penyebab_masalah": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Jelaskan akar penyebab masalah berdasarkan analisis...",
                }
            ),
            "tindakan_dilakukan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Jelaskan tindakan yang telah dilakukan untuk mengatasi masalah...",
                }
            ),
            "tindakan_pencegahan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Jelaskan tindakan pencegahan untuk mencegah masalah serupa...",
                }
            ),
            "dokumentasi_sebelum": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*,.pdf,.dwg"}
            ),
            "dokumentasi_sesudah": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*,.pdf,.dwg"}
            ),
            # Checkbox styling untuk faktor 4M1E
            "faktor_man": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "faktor_material": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "faktor_machine": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "faktor_method": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "faktor_environment": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
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
            "dokumentasi_sebelum": "Dokumentasi Sebelum (Max 1MB)",
            "dokumentasi_sesudah": "Dokumentasi Sesudah (Max 1MB)",
        }

    def clean_dokumentasi_sebelum(self):
        file = self.cleaned_data.get("dokumentasi_sebelum")
        if file:
            if file.size > 1024 * 1024:  # 1MB
                raise forms.ValidationError("File size tidak boleh lebih dari 1MB")
        return file

    def clean_dokumentasi_sesudah(self):
        file = self.cleaned_data.get("dokumentasi_sesudah")
        if file:
            if file.size > 1024 * 1024:  # 1MB
                raise forms.ValidationError("File size tidak boleh lebih dari 1MB")
        return file


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
        # Filter leader choices untuk yang memiliki kuota tersedia
        available_leaders = User.objects.filter(
            role="leader",
            leader_quota__isnull=False,
            leader_quota__is_active=True,
        ).filter(
            models.Q(
                leader_quota__current_foreman_count__lt=models.F(
                    "leader_quota__max_foreman"
                )
            )
        )

        self.fields["leader"].queryset = available_leaders
        self.fields["leader"].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        leader = cleaned_data.get("leader")

        if role == "foreman":
            if not leader:
                raise forms.ValidationError("Foreman harus memiliki leader.")

            # Validasi kuota leader
            if leader.leader_quota and not leader.leader_quota.can_add_foreman():
                raise forms.ValidationError(
                    f"Leader {leader.name} sudah mencapai kuota maksimum foreman."
                )

        elif role == "leader":
            if leader:
                raise forms.ValidationError("Leader tidak boleh memiliki leader.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # Jika membuat leader baru, buat LeaderQuota
            if user.role == "leader":
                LeaderQuota.objects.get_or_create(
                    leader_name=user.name or user.username,
                    defaults={"max_foreman": 0},  # Admin harus set kuota manual
                )

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
