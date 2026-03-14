from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceCategory(models.Model):
    """
    Категория медицинских услуг
    """
    name = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'), blank=True)
    order = models.PositiveIntegerField(_('порядок отображения'), default=0)
    is_active = models.BooleanField(_('активна'), default=True)
    
    class Meta:
        verbose_name = _('категория услуги')
        verbose_name_plural = _('категории услуг')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

    def get_main_image(self):
        return self.images.filter(is_main=True).first()

    def get_fallback_image(self):
        return self.images.first()


class Service(models.Model):
    """
    Медицинская услуга
    """
    name = models.CharField(_('название'), max_length=200)
    category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.CASCADE, 
        related_name='services',
        verbose_name=_('категория')
    )
    description = models.TextField(_('описание'))
    short_description = models.TextField(_('краткое описание'), max_length=500)
    price = models.DecimalField(_('цена'), max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(_('длительность (минут)'), default=30)
    preparation = models.TextField(
        _('подготовка к процедуре'), 
        blank=True,
        help_text=_('Инструкции по подготовке к диагностической процедуре')
    )
    results_time = models.CharField(
        _('время получения результатов'), 
        max_length=100,
        blank=True,
        help_text=_('Например: "через 1-2 дня", "в течение часа" и т.д.')
    )
    order = models.PositiveIntegerField(_('порядок отображения'), default=0)
    is_active = models.BooleanField(_('активна'), default=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('медицинская услуга')
        verbose_name_plural = _('медицинские услуги')
        ordering = ['category', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.category.name})'
    
    @property
    def price_formatted(self):
        """
        Форматированная цена с разделением тысяч
        """
        return f'{self.price:,.0f}'.replace(',', ' ')


class ServiceImage(models.Model):
    """
    Изображение для категории медицинской услуги
    """
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name=_('категория услуги')
    )
    image = models.ImageField(
        _('изображение'), 
        upload_to='service_images/'
    )
    is_main = models.BooleanField(
        _('основное изображение'), 
        default=False,
        help_text=_('Отметьте, если это основное изображение для категории услуги')
    )
    order = models.PositiveIntegerField(_('порядок отображения'), default=0)
    
    class Meta:
        verbose_name = _('изображение категории услуги')
        verbose_name_plural = _('изображения категорий услуг')
        ordering = ['order']
    
    def __str__(self):
        return f'Изображение для {self.category.name}'