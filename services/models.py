from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from MedCheck import settings


class ServiceCategory(models.Model):
    """
    Категория медицинских услуг
    """

    name = models.CharField(_("название"), max_length=100)
    description = models.TextField(_("описание"), blank=True)
    order = models.PositiveIntegerField(_("порядок отображения"), default=0)
    is_active = models.BooleanField(_("активна"), default=True)

    class Meta:
        verbose_name = _("категория услуги")
        verbose_name_plural = _("категории услуг")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    image = models.ImageField(
        _("изображение"), upload_to="service_category_images/", blank=True, null=True
    )

    def get_main_image(self):
        if self.image:
            return self.image
        return self.get_fallback_image()

    def get_fallback_image(self):
        return self.image


class Service(models.Model):
    """
    Медицинская услуга
    """

    name = models.CharField(_("название"), max_length=200)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name=_("категория"),
    )
    description = models.TextField(_("описание"))
    short_description = models.TextField(_("краткое описание"), max_length=500)
    price = models.DecimalField(_("цена"), max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(_("длительность (минут)"), default=30)
    preparation = models.TextField(
        _("подготовка к процедуре"),
        blank=True,
        help_text=_("Инструкции по подготовке к диагностической процедуре"),
    )
    results_time = models.CharField(
        _("время получения результатов"),
        max_length=100,
        blank=True,
        help_text=_('Например: "через 1-2 дня", "в течение часа" и т.д.'),
    )
    order = models.PositiveIntegerField(_("порядок отображения"), default=0)
    is_active = models.BooleanField(_("активна"), default=True)
    created_at = models.DateTimeField(_("дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("дата обновления"), auto_now=True)

    doctors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Врачи",
        blank=True,
        related_name="services_as_doctor",
    )

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def price_formatted(self):
        """
        Форматированная цена с разделением тысяч
        """
        return f"{self.price:,.0f}".replace(",", " ")

    class Meta:
        verbose_name = _("медицинская услуга")
        verbose_name_plural = _("медицинские услуги")
        ordering = ["category", "name"]


class DoctorSchedule(models.Model):
    """
    График работы врача
    """

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Врач",
        related_name="schedules",
    )
    day_of_week = models.PositiveSmallIntegerField(
        "День недели",
        choices=[
            (0, "Понедельник"),
            (1, "Вторник"),
            (2, "Среда"),
            (3, "Четверг"),
            (4, "Пятница"),
            (5, "Суббота"),
            (6, "Воскресенье"),
        ],
    )
    time_of_day = models.PositiveSmallIntegerField(
        "Часы приема",
        choices=[
            (0, "09:00"),
            (1, "09:30"),
            (2, "10:00"),
            (3, "10:30"),
            (4, "11:00"),
            (5, "11:30"),
            (6, "12:00"),
            (7, "12:30"),
            (8, "13:00"),
            (9, "13:30"),
            (10, "14:00"),
            (11, "14:30"),
            (12, "15:00"),
            (13, "15:30"),
            (14, "16:00"),
            (15, "16:30"),
            (16, "17:00"),
        ],
    )
    is_active = models.BooleanField("Активно", default=True)

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()}: {self.get_time_of_day_display()}"

    @property
    def start_datetime(self):
        """
        Возвращает полную дату и время начала приема
        """
        from datetime import datetime, timedelta

        # Берем базовую дату (понедельник)
        base_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
        # Добавляем день недели
        appointment_date = base_date + timedelta(days=self.day_of_week)
        # Добавляем время
        hour = 9 + (self.time_of_day // 2)  # Начало с 9:00
        minute = 0 if self.time_of_day % 2 == 0 else 30  # 0 или 30 минут
        return datetime.combine(
            appointment_date, datetime.min.time().replace(hour=hour, minute=minute)
        )

    @property
    def end_datetime(self):
        """
        Возвращает полную дату и время окончания приема
        """
        from datetime import timedelta

        duration = timedelta(minutes=30)  # Длительность приема 30 минут
        return self.start_datetime + duration

    class Meta:
        verbose_name = "График работы врача"
        verbose_name_plural = "Графики работы врачей"
        unique_together = ["doctor", "day_of_week", "time_of_day"]
        ordering = ["day_of_week", "time_of_day"]


class Appointment(models.Model):
    """
    Запись на приём
    """

    @classmethod
    def is_slot_available(cls, doctor, scheduled_at):
        """
        Проверяет доступность слота для записи
        """
        # Проверяем, есть ли уже активная запись на это время
        return not cls.objects.filter(
            doctor=doctor,
            scheduled_at=scheduled_at,
            is_active=True
        ).exists()

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пациент"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name="Услуга"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Врач",
        related_name="appointments_as_doctor",
    )
    scheduled_at = models.DateTimeField("Запланировано на", null=True, blank=True)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)

    @classmethod
    def get_available_slots(cls, doctor, date):
        """
        Возвращает доступные слоты для записи на приём
        """
        # Получаем день недели для заданной даты
        day_of_week = date.weekday()

        # Получаем все доступные слоты из графика врача для этого дня недели
        schedule_slots = DoctorSchedule.objects.filter(
            doctor=doctor, day_of_week=day_of_week, is_active=True
        ).order_by("time_of_day")

        # Получаем все уже занятые слоты на эту дату
        booked_slots = cls.objects.filter(
            doctor=doctor, scheduled_at__date=date, is_active=True
        ).values_list("scheduled_at", flat=True)

        # Преобразуем занятые слоты в datetime объекты для сравнения
        booked_datetimes = [slot for slot in booked_slots]

        available_slots = []
        for slot in schedule_slots:
            # Создаем datetime объект для слота
            slot_datetime = slot.start_datetime.replace(
                year=date.year, month=date.month, day=date.day
            )

            # Проверяем, что слот еще не занят
            if slot_datetime not in booked_datetimes:
                available_slots.append(
                    {
                        "datetime": slot_datetime,
                        "display": slot.get_time_of_day_display(),
                    }
                )

        return available_slots

    class Meta:
        verbose_name = "Запись на приём"
        verbose_name_plural = "Записи на приём"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Запись: {self.patient} к {self.doctor} на {self.scheduled_at}"



class DiagnosisResult(models.Model):
    """
    Результат диагностики
    """

    appointment = models.ForeignKey(
        "Appointment",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Запись на приём",
        related_name="diagnosis_results",
    )
    file = models.FileField(
        "Файл с результатами",
        upload_to="diagnosis_results/",
        help_text="файл с результатами диагностики",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        default="processing",
        choices=[
            ("processing", "В обработке"),
            ("completed", "Готово"),
            ("failed", "Ошибка"),
        ],
    )
    uploaded_at = models.DateTimeField("Дата загрузки", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    description = models.TextField(
        "Описание",
        blank=True,
        null=True,
        help_text="Дополнительные комментарии к результатам",
    )

    @property
    def patient(self):
        """
        Возвращает пациента из связанной записи на приём
        """
        return self.appointment.patient if self.appointment else None

    def __str__(self):
        return f"Результат {self.appointment} - {self.get_status_display()}"

    def get_file_url(self):
        return self.file.url if self.file else None

    def is_ready(self):
        return self.status == "completed"

    class Meta:
        verbose_name = "Результат диагностики"
        verbose_name_plural = "Результаты диагностики"
        ordering = ["-uploaded_at"]
