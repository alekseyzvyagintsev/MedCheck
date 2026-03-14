from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Service, ServiceCategory


def category_list(request):
    """
    Страница категорий услуг с единым поиском по услугам
    """
    # Получаем все активные услуги для поиска
    services_list = Service.objects.filter(is_active=True).order_by('order')
    
    # Поиск по названию и описанию услуги
    search_query = request.GET.get('search')
    if search_query:
        services_list = services_list.filter(
            Q(name__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Получаем все категории для отображения
    categories = ServiceCategory.objects.prefetch_related('images').all()
    
    return render(request, 'services/categories.html', {
        'categories': categories,
        'services_list': services_list,
        'search_query': search_query
    })


def services(request):
    """
    Страница всех активных услуг с поиском
    """
    services_list = Service.objects.filter(is_active=True).order_by('order')
    
    return render(request, 'services/services.html', {
        'services': services_list
    })

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