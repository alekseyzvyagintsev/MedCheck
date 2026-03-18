from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone

from ..models import Appointment, Service

User = get_user_model()


def parse_datetime_string(datetime_str):
    """
    Парсит строку даты и времени в aware datetime объект
    Ожидаемый формат: '2026-03-18 09:00:00'
    """
    try:
        # Сначала парсим как naive datetime
        naive_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        # Преобразуем в aware datetime с использованием часового пояса
        return timezone.make_aware(naive_dt)
    except ValueError as e:
        raise ValueError(f"Некорректный формат даты и времени: {str(e)}")


def validate_appointment_time(scheduled_at):
    """
    Проверяет, что время записи в будущем
    """
    if scheduled_at <= timezone.now():
        raise ValueError("Нельзя записаться на прошедшее время и дату")
    return True


def render_appointment_step(request, template, context):
    """
    Унифицированная функция для рендеринга шагов записи
    """
    return render(request, template, context)


def render_error(request, error_message):
    """
    Унифицированная функция для рендеринга ошибок
    """
    return render(request, "services/steps/error.html", {"error": error_message})


def create_appointment_logic(patient, service_id, doctor_id, scheduled_at):
    """
    Бизнес-логика создания записи на приём.
    Принимает готовый datetime объект
    """
    try:
        # Получаем модели
        service = Service.objects.get(id=service_id)
        doctor = User.objects.get(id=doctor_id)

        # Проверяем доступность слота
        if not Appointment.is_slot_available(doctor, scheduled_at):
            return False, {
                "error": "Выбранный слот недоступен. Пожалуйста, выберите другое время."
            }

        # Проверяем, что дата и время в будущем
        if scheduled_at <= timezone.now():
            return False, {"error": "Нельзя записаться на прошедшее время и дату"}

        # Создаём запись
        appointment = Appointment.objects.create(
            patient=patient,
            service=service,
            doctor=doctor,
            scheduled_at=scheduled_at,

        )



        return True, {
            "success": True,
            "message": "Запись успешно создана!",
            "appointment_id": appointment.id,
        }

    except Service.DoesNotExist:
        return False, {"error": "Услуга не найдена"}
    except User.DoesNotExist:
        return False, {"error": "Врач не найден"}
    except Exception as e:
        return False, {"error": f"Ошибка при создании записи: {str(e)}"}


def delete_appointment_logic(appointment_id, user):
    """
    Бизнес-логика удаления записи на приём
    """
    try:
        # Получаем запись
        appointment = Appointment.objects.select_related(
            "patient", "doctor", "service"
        ).get(id=appointment_id)

        # Проверяем права доступа
        if appointment.patient != user and appointment.doctor != user:
            return False, {"error": "У вас нет прав для отмены этой записи"}

        # Проверяем, что запись активна
        if not appointment.is_active:
            return False, {"error": "Запись уже отменена"}

        # Проверяем, что запись в будущем
        if appointment.scheduled_at <= timezone.now():
            return False, {"error": "Нельзя отменить прошедшую запись"}

        # Деактивируем запись
        appointment.is_active = False
        appointment.status = "cancelled"
        appointment.save()



        return True, {"success": True, "message": "Запись успешно отменена!"}

    except Appointment.DoesNotExist:
        return False, {"error": "Запись не найдена"}
    except Exception as e:
        return False, {"error": f"Ошибка при отмене записи: {str(e)}"}
