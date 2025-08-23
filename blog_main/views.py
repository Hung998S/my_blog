# blog_main/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout


@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirmPassword', '').strip()

        # Kiểm tra thông tin
        if not username or not email or not password or not confirm_password:
            messages.error(request, "Vui lòng điền đầy đủ thông tin.")
            return redirect('home')

        if password != confirm_password:
            messages.error(request, "Mật khẩu không khớp.")
            return redirect('home')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tài khoản đã tồn tại.")
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng.")
            return redirect('home')

        # Tạo user mới
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Đăng ký thành công! Bạn có thể đăng nhập ngay.")
        return redirect('home')  # quay lại home để modal login hiển thị

    return redirect('home')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Chào mừng {username}!")
            return redirect('home')
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu!")
            return redirect('home')

    return redirect('home')


# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Đăng xuất thành công!")
    return redirect('home')


