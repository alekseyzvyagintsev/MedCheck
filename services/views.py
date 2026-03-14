from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


def category_list(request):
    """
    Страница категорий услуг
    """
    categories = ServiceCategory.objects.prefetch_related('images').all()
    return render(request, 'services/categories.html', {'categories': categories})


def services(request):
    """
    Страница всех активных услуг
    """
    services_list = Service.objects.filter(is_active=True).order_by('order')
    return render(request, 'services/services.html', {'services': services_list})

def category_services(request, category_id):
    """
    Страница услуг определенной категории
    """
    category = get_object_or_404(ServiceCategory, id=category_id)
    services_list = Service.objects.filter(category=category, is_active=True).order_by('order')
    return render(request, 'services/services.html', {'services': services_list, 'category': category})


def service_detail(request, service_id):
    """
    Детальная страница услуги
    """
    service = get_object_or_404(Service, id=service_id, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})