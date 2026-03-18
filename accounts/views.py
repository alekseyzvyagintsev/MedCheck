from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from services.models import Appointment, DiagnosisResult

from .forms import UserProfileForm, UserRegistrationForm


def register(request):
    """
    Регистрация нового пользователя (только пациенты)
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Аутентификация и вход пользователя
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)

            messages.success(request, "Вы успешно зарегистрировались как пациент!")
            return redirect("accounts:profile")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """
    Просмотр и редактирование профиля
    """
    # Проверяем, может ли пользователь просматривать этот профиль
    # Убрал проверку, так как она была некорректной (всегда возвращает False)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)

    # Получаем записи на приём пользователя как пациента
    active_appointments = Appointment.objects.filter(
        patient=request.user,
        is_active=True,
        scheduled_at__gte=timezone.now()
    ).select_related('service', 'doctor')

    # Получаем результаты диагностики пользователя
    diagnosis_results = DiagnosisResult.objects.filter(
        appointment__patient=request.user
    ).select_related('appointment__service', 'appointment__doctor').order_by('-uploaded_at')

    return render(request, "accounts/profile.html", {
        "form": form,
        "active_appointments": active_appointments,
        "diagnosis_results": diagnosis_results
    })


@login_required
def create_doctor(request):
    """
    Создание нового врача (только для персонала)
    """
    # Проверяем, является ли пользователь персоналом
    if not request.user.is_staff:
        raise Http404("У вас нет прав для создания врачей")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Устанавливаем is_staff=True для врачей
            user.is_staff = True
            user.save()

            messages.success(request, f"Врач {user.username} успешно создан!")
            return redirect("services:dashboard")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/create_doctor.html", {"form": form})


# Используем встроенные представления Django для входа и выхода
login_view = auth_views.LoginView.as_view(template_name="accounts/login.html")


# Просто перенаправляем на главную страницу
def logout_view(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect

    logout(request)
    return redirect("main:home")


@login_required
def delete_profile(request):
    """
    Удаление профиля пользователя
    """
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Ваш аккаунт успешно удален")
        return redirect("main:home")
    
    return redirect("accounts:profile")