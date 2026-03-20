from datetime import timedelta

from django.utils import timezone

from services.models import DoctorSchedule


def create_doctor_schedule(doctor):
    """
    Создает график работы для врача на 3 недели вперед
    """
    # Создаем график на 3 недели вперед (текущая и 2 следующие недели)
    today = timezone.now().date()
    start_date = today - timedelta(
        days=today.weekday()
    )  # Начало текущей недели (понедельник)

    for week_offset in [0, 1, 2]:  # Текущая неделя и следующие 2 недели
        week_start = start_date + timedelta(weeks=week_offset)

        # Создаем слоты на каждый день недели (пн-пт)
        for day in range(5):  # Понедельник-пятница
            date = week_start + timedelta(days=day)

            # Создаем слоты с 9:00 до 17:00 с интервалом 30 минут
            for hour in range(9, 17):
                for minute in [0, 30]:
                    # Создаем объект DoctorSchedule
                    DoctorSchedule.objects.get_or_create(
                        doctor=doctor,
                        day_of_week=date.weekday(),
                        time_of_day=get_time_of_day(hour, minute),
                        defaults={"is_active": True},
                    )


def get_time_of_day(hour, minute):
    """
    Возвращает соответствующее значение time_of_day для заданного времени
    """
    time_slots = [
        (9, 0),
        (9, 30),
        (10, 0),
        (10, 30),
        (11, 0),
        (11, 30),
        (12, 0),
        (12, 30),
        (13, 0),
        (13, 30),
        (14, 0),
        (14, 30),
        (15, 0),
        (15, 30),
        (16, 0),
        (16, 30),
        (17, 0),
    ]
    try:
        return time_slots.index((hour, minute))
    except ValueError:
        return 0  # По умолчанию 9:00 если время не найдено


def assign_doctor_group(user):
    """
    Назначает пользователю группу 'доктор'
    """
    # Импортируем Group внутри функции, чтобы избежать циклической зависимости
    from django.contrib.auth.models import Group

    doctor_group, created = Group.objects.get_or_create(name="доктор")
    user.groups.add(doctor_group)
    user.save()
