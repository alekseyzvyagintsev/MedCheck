import json
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from content.content import get_common_context
from services.utils import (create_appointment_logic, delete_appointment_logic,
                            parse_datetime_string, render_appointment_step,
                            render_error, validate_appointment_time)

from .forms import DiagnosisResultForm
from .models import Appointment, DiagnosisResult, Service, ServiceCategory

User = get_user_model()


@login_required
def diagnosis_result_detail(request, appointment_id):
    """
    Просмотр детальной информации о результате диагностики
    """
    # Получаем результат диагностики через связь с записью на прием
    result = DiagnosisResult.objects.select_related(
        "appointment__patient", "appointment__service", "appointment__doctor"
    ).get(appointment__id=appointment_id, appointment__patient=request.user)

    context = get_common_context()
    context = {**context, "result": result}
    return render(request, "services/diagnosis_result_detail.html", context)


def category_list(request):
    """
    Страница категорий услуг с единым поиском по услугам
    """
    # Получаем все активные услуги для поиска
    services_list = Service.objects.filter(is_active=True).order_by("order")

    # Поиск по названию и описанию услуги
    search_query = request.GET.get("search")
    if search_query:
        services_list = services_list.filter(
            Q(name__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    # Получаем все категории для отображения
    categories = ServiceCategory.objects.all()

    context = get_common_context()
    context = {
        **context,
        "categories": categories,
        "services_list": services_list,
        "search_query": search_query,
    }
    return render(request, "services/categories.html", context)


def services(request):
    """
    Страница всех активных услуг с поиском
    """
    services_data = Service.objects.filter(is_active=True).order_by("order")

    context = get_common_context()
    context = {**context, "services": services_data}
    return render(request, "services/services.html", context)


def category_services(request, category_id):
    """
    Страница услуг определенной категории
    """
    category = get_object_or_404(ServiceCategory, id=category_id)
    services_data = Service.objects.filter(category=category, is_active=True).order_by(
        "order"
    )
    context = get_common_context()
    context = {**context, "services": services_data, "category": category}
    return render(request, "services/services.html", context)


def service_detail(request, service_id):
    """
    Детальная страница услуги
    """
    service = get_object_or_404(Service, id=service_id, is_active=True)
    context = get_common_context()
    context = {**context, "service": service}
    return render(request, "services/service_detail.html", context)


@login_required
@require_http_methods(["GET"])
def get_services(request):
    """
    Отображение страницы выбора услуги
    """
    services_data = Service.objects.filter(is_active=True)
    context = get_common_context()
    context = {**context, "services": services_data}
    return render_appointment_step(
        request, "services/steps/step1_choose_service.html", context
    )


@login_required
@require_http_methods(["POST"])
def choose_service(request):
    """
    Обработка выбора услуги и переход к выбору врача
    """
    try:
        service_id = request.POST.get("service_id")
        service = Service.objects.get(id=service_id)

        # Получаем врачей, связанных с этой услугей
        doctors_list = service.doctors.filter(is_active=True)

        context = get_common_context()
        context = {**context, "service": service, "doctors": doctors_list}
        return render_appointment_step(
            request, "services/steps/step2_choose_doctor.html", context
        )
    except Service.DoesNotExist:
        return render_error(request, "Услуга не найдена")
    except Exception as e:
        return render_error(request, str(e))


@login_required
@require_http_methods(["POST"])
def choose_doctor(request):
    """
    Обработка выбора врача и переход к выбору даты
    """
    try:
        doctor_id = request.POST.get("doctor_id")
        service_id = request.POST.get("service_id")

        doctor = User.objects.get(id=doctor_id)
        service = Service.objects.get(id=service_id)

        context = get_common_context()
        context = {**context, "doctor": doctor, "service": service}
        return render_appointment_step(
            request, "services/steps/step3_choose_date.html", context
        )
    except User.DoesNotExist:
        return render_error(request, "Врач не найден")
    except Service.DoesNotExist:
        return render_error(request, "Услуга не найдена")
    except Exception as e:
        return render_error(request, str(e))


@login_required
@require_http_methods(["POST"])
def choose_date(request):
    """
    Обработка выбора даты и переход к выбору времени
    """
    try:
        doctor_id = request.POST.get("doctor_id")
        service_id = request.POST.get("service_id")
        date_str = request.POST.get("date")

        doctor = User.objects.get(id=doctor_id)
        service = Service.objects.get(id=service_id)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Получаем доступные слоты
        available_slots = Appointment.get_available_slots(doctor, date)

        context = get_common_context()
        context = {
            **context,
            "doctor": doctor,
            "service": service,
            "date": date,
            "slots": available_slots,
        }
        return render_appointment_step(
            request, "services/steps/step4_choose_time.html", context
        )
    except User.DoesNotExist:
        return render_error(request, "Врач не найден")
    except Service.DoesNotExist:
        return render_error(request, "Услуга не найдена")
    except ValueError:
        return render_error(request, "Некорректный формат даты")
    except Exception as e:
        return render_error(request, str(e))


@login_required
@require_http_methods(["POST"])
def confirm_appointment(request):
    """
    Подтверждение записи и создание её в базе данных
    """
    try:
        service_id = request.POST.get("service_id")
        doctor_id = request.POST.get("doctor_id")
        scheduled_at_str = request.POST.get("scheduled_at")

        # Парсим дату и время из строки
        try:
            scheduled_at = parse_datetime_string(scheduled_at_str)
        except ValueError as e:
            return render_error(request, str(e))

        # Проверяем, что время в будущем
        try:
            validate_appointment_time(scheduled_at)
        except ValueError as e:
            return render_error(request, str(e))

        # Вызываем бизнес-логику создания записи
        success, result = create_appointment_logic(
            patient=request.user,
            service_id=service_id,
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
        )

        if success:
            context = get_common_context()
            context = {**context, "appointment_id": result["appointment_id"]}
            return render_appointment_step(
                request, "services/steps/step5_confirmation.html", context
            )
        else:
            return render_error(request, result["error"])

    except Exception as e:
        return render_error(request, str(e))


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_appointment(request):
    """
    Создание записи на приём
    """
    try:
        data = json.loads(request.body)

        # Получаем данные из запроса
        service_id = data.get("service_id")
        doctor_id = data.get("doctor_id")
        scheduled_at = data.get("scheduled_at")

        # Парсим дату и время, если получили строку
        if isinstance(scheduled_at, str):
            try:
                scheduled_at = parse_datetime_string(scheduled_at)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

        # Вызываем бизнес-логику создания записи
        success, result = create_appointment_logic(
            patient=request.user,
            service_id=service_id,
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
        )

        if success:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def delete_appointment(request, appointment_id):
    """
    Удаление записи на приём через POST-запрос
    """
    if request.method == "POST":
        try:
            # Вызываем бизнес-логику удаления записи
            success, result = delete_appointment_logic(
                appointment_id=appointment_id, user=request.user
            )

            if success:
                messages.success(request, result["message"])
            else:
                messages.error(request, result["error"])

        except Exception as e:
            messages.error(request, f"Ошибка при отмене записи: {str(e)}")

        return redirect("accounts:profile")

    return JsonResponse({"error": "Метод не разрешен"}, status=405)


@login_required
@require_http_methods(["GET"])
def get_available_slots(request, doctor_id):
    """
    Получение доступных слотов для записи на приём
    """
    try:
        # Получаем дату из параметров запроса
        date_str = request.GET.get("date")
        if not date_str:
            return JsonResponse({"error": "Не указана дата"}, status=400)

        # Преобразуем строку в объект даты
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Некорректный формат даты"}, status=400)

        # Получаем врача
        doctor = get_object_or_404(get_user_model(), id=doctor_id)

        # Получаем доступные слоты через метод модели
        available_slots = Appointment.get_available_slots(doctor, date)

        return JsonResponse({"success": True, "slots": available_slots})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def doctor_dashboard(request):
    """
    Кабинет врача с отображением записей на сегодня
    """
    # Проверяем, является ли пользователь врачом (персоналом)
    if not request.user.is_staff:
        raise Http404("У вас нет прав для доступа к кабинету врача")

    # Получаем сегодняшнюю дату
    today = date.today()

    # Получаем записи на сегодня для этого врача
    today_appointments = (
        Appointment.objects.filter(
            doctor=request.user, scheduled_at__date=today, is_active=True
        )
        .select_related("patient", "service")
        .order_by("scheduled_at")
    )

    context = get_common_context()
    context = {**context, "today_appointments": today_appointments}
    return render(request, "services/doctor/dashboard.html", context)


@login_required
def create_diagnosis_result(request, appointment_id):
    """
    Создание результата обследования для записи
    """
    # Проверяем, является ли пользователь врачом
    if not request.user.is_staff:
        raise Http404("У вас нет прав для создания результатов обследования")

    # Получаем запись на приём
    appointment = get_object_or_404(
        Appointment.objects.select_related("patient", "doctor", "service"),
        id=appointment_id,
        doctor=request.user,
    )

    # Проверяем, существует ли уже результат для этой записи
    if (
        hasattr(appointment, "diagnosis_results")
        and appointment.diagnosis_results.exists()
    ):
        messages.warning(
            request, "Результат обследования для этой записи уже существует"
        )
        return redirect("services:view_result", appointment_id=appointment_id)

    if request.method == "POST":
        form = DiagnosisResultForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаем результат диагностики
            diagnosis_result = form.save(commit=False)
            diagnosis_result.appointment = appointment
            diagnosis_result.save()

            messages.success(request, "Результат обследования успешно создан")
            return redirect("services:view_result", appointment_id=appointment_id)
    else:
        form = DiagnosisResultForm()

    context = get_common_context()
    context = {
        **context,
        "form": form,
        "title": f"Создание результата для {appointment.patient.get_full_name() or appointment.patient.username}",
        "appointment": appointment,
    }
    return render(request, "services/doctor/result_form.html", context)


@login_required
def view_diagnosis_result(request, appointment_id):
    """
    Просмотр результата обследования
    """
    # Получаем результат диагностики
    diagnosis_result = get_object_or_404(
        DiagnosisResult.objects.select_related(
            "appointment__patient", "appointment__doctor", "appointment__service"
        ),
        appointment__id=appointment_id,
    )

    # Проверяем права доступа: врач может просматривать только свои результаты,
    # админ может просматривать все
    if (
        diagnosis_result.appointment.doctor != request.user
        and not request.user.is_superuser
    ):
        raise PermissionDenied("У вас нет прав для просмотра этого результата")

    context = get_common_context()
    context = {**context, "result": diagnosis_result}
    return render(request, "services/doctor/result_detail.html", context)


@login_required
def edit_diagnosis_result(request, appointment_id):
    """
    Редактирование результата обследования
    """
    # Получаем результат диагностики
    diagnosis_result = get_object_or_404(
        DiagnosisResult.objects.select_related("appointment__doctor"),
        appointment__id=appointment_id,
    )

    # Проверяем права доступа: только владелец (врач) или админ может редактировать
    if (
        diagnosis_result.appointment.doctor != request.user
        and not request.user.is_superuser
    ):
        raise PermissionDenied("У вас нет прав для редактирования этого результата")

    if request.method == "POST":
        form = DiagnosisResultForm(
            request.POST, request.FILES, instance=diagnosis_result
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Результат обследования успешно обновлен")
            return redirect("services:view_result", appointment_id=appointment_id)
    else:
        form = DiagnosisResultForm(instance=diagnosis_result)

    context = get_common_context()
    context = {
        **context,
        "form": form,
        "title": f"""
        Редактирование результата для {diagnosis_result.appointment.patient.get_full_name()
                                       or diagnosis_result.appointment.patient.username}
        """,
        "appointment": diagnosis_result.appointment,
        "result": diagnosis_result,
    }
    return render(request, "services/doctor/result_form.html", context)


@login_required
def delete_diagnosis_result(request, appointment_id):
    """
    Удаление результата обследования
    """
    # Получаем результат диагностики
    diagnosis_result = get_object_or_404(
        DiagnosisResult.objects.select_related("appointment__doctor"),
        appointment__id=appointment_id,
    )

    # Проверяем права доступа: только владелец (врач) или админ может удалить
    if (
        diagnosis_result.appointment.doctor != request.user
        and not request.user.is_superuser
    ):
        raise PermissionDenied("У вас нет прав для удаления этого результата")

    if request.method == "POST":
        diagnosis_result.delete()
        messages.success(request, "Результат обследования успешно удален")

    return redirect("services:dashboard")
