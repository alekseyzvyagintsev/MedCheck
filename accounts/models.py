from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Почта")
    username = models.CharField(
        max_length=30, unique=True, verbose_name="Имя пользователя"
    )
    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Номер телефона"
    )
    date_of_birth = models.DateField(
        null=True, blank=True, default=None, verbose_name="Дата рождения"
    )
    address = models.TextField(
        max_length=200, blank=True, null=True, verbose_name="Адрес"
    )
    image = models.ImageField(
        upload_to="user_images/", blank=True, null=True, verbose_name="Фото"
    )

    def __str__(self):
        return f"{self.username} - {self.email}"

    def save(self, *args, **kwargs):
        # Флаг для определения, создается ли объект впервые
        is_new = self.pk is None

        # Сначала сохраняем пользователя, чтобы получить pk
        super().save(*args, **kwargs)

        # Проверяем, является ли пользователь персоналом и создается впервые
        if is_new and self.is_staff:
            # Назначаем группу 'доктор' и создаем график работы
            # Импортируем внутри функции для избежания циклического импорта
            from services.utils.doctors import (assign_doctor_group,
                                                create_doctor_schedule)
            assign_doctor_group(self)
            create_doctor_schedule(self)

            # Обновляем пользователя после добавления в группу
            self.refresh_from_db()
