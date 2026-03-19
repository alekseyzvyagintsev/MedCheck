from django.db import models


class Fragment(models.Model):
    """
    Модель фрагмента страницы
    """

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.CharField(
        max_length=255, verbose_name="Описание", blank=True, null=True
    )
    content = models.TextField(verbose_name="Содержимое")
    image = models.ImageField(
        upload_to="images/", verbose_name="Изображение", blank=True, null=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.title} - {self.description} - изменен: {self.updated_at}"

    class Meta:
        verbose_name = "Фрагмент"
        verbose_name_plural = "Фрагменты"
        ordering = ["-title"]
