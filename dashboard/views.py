from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models  # Tambahkan ini
# Atau lebih spesifik:
# from django.db.models import Q
from .forms import LoginForm, RegisterForm, EmployeeRegistrationForm
from .models import User


def hello_world(request):
    return render(request, 'hello.html')


def hello_template(request):
    return render(request, 'hello_template.html')


def hello_world_tailwind(request):
    """View untuk demo Tailwind CSS"""
    return render(request, 'hello-world.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Username atau password salah.')
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('login')
        else:
            messages.error(request, 'Terjadi kesalahan dalam pendaftaran.')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


# NEW: Admin functions
def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@user_passes_test(is_admin)
def employee_list(request):
    """Daftar semua karyawan untuk admin"""
    employees = User.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query) |  # noqa: F821
            models.Q(name__icontains=search_query) |
            models.Q(nrp__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(employees, 10)  # 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'search_query': search_query,
        'total_employees': employees.count(),
    }
    return render(request, 'admin/employee_list.html', context)

@user_passes_test(is_admin)
def employee_create(request):
    """Form untuk admin menambah karyawan baru"""
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Karyawan {employee.username} berhasil didaftarkan!')
            return redirect('employee_list')
        else:
            messages.error(request, 'Terjadi kesalahan dalam pendaftaran karyawan.')
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'admin/employee_create.html', {'form': form})

@user_passes_test(is_admin)
def employee_detail(request, user_id):
    """Detail karyawan"""
    employee = get_object_or_404(User, id=user_id)
    return render(request, 'admin/employee_detail.html', {'employee': employee})

@user_passes_test(is_admin)
def employee_edit(request, user_id):
    """Edit data karyawan"""
    employee = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data karyawan {employee.username} berhasil diupdate!')
            return redirect('employee_detail', user_id=employee.id)
        else:
            messages.error(request, 'Terjadi kesalahan dalam update data.')
    else:
        form = EmployeeRegistrationForm(instance=employee)
    
    return render(request, 'admin/employee_edit.html', {'form': form, 'employee': employee})

@user_passes_test(is_admin)
def employee_delete(request, user_id):
    """Hapus karyawan"""
    employee = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = employee.username
        employee.delete()
        messages.success(request, f'Karyawan {username} berhasil dihapus!')
        return redirect('employee_list')
    
    return render(request, 'admin/employee_delete.html', {'employee': employee})
