from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from orders.models import Order

def register(request):
    if request.user.is_authenticated:
        return redirect('main:catalog')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main:catalog')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('main:catalog')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:catalog')
            else:
                messages.error(request, 'Неверный email или пароль')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})

@login_required(login_url="/users/login")
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('users:login')

@login_required(login_url="/users/login")
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'users/profile.html', {
        'form': form,
        'orders': orders,
    })
