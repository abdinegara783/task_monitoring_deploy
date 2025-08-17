import email
from typing import Required
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets
from .models import User as CustomUser
from .models import User, ActivityReport


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
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                "placeholder": "Masukkan password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Konfirmasi Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400",
                "placeholder": "Konfirmasi password",
            }
        ),
    )

    class Meta:
        model = CustomUser
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
            "role": forms.Select(
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
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password tidak cocok")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ActivityReportForm(forms.ModelForm):
    """Form untuk membuat Activity Report"""

    class Meta:
        model = ActivityReport
        fields = [
            "date",
            "leader",
            "Unit_Code",
            "Hmkm",
            "start_time",
            "end_time",
            "component",
            "activities",
            "activities_code",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input-field block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200",
                }
            ),
            "leader": forms.Select(
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
            "leader": "Group Leader",
            "Unit_Code": "Unit Code",
            "Hmkm": "HM/KM",
            "start_time": "Waktu Mulai",
            "end_time": "Waktu Selesai",
            "component": "Component",
            "activities": "Activity",
            "activities_code": "Activity Code",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set default date to today
        if not self.instance.pk:
            from django.utils import timezone

            self.fields["date"].initial = timezone.now().date()
