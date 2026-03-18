from django.shortcuts import render

from services.models import ServiceCategory


def home(request):
    """
    Главная страница
    """
    categories = ServiceCategory.objects.all()
    return render(
        request,
        "main/home.html",
        {"categories": categories, "category_list_url": "services:category_list"},
    )


def about(request):
    """
    Страница "О компании"
    """
    return render(request, "main/about.html")


def contact(request):
    """
    Страница контактов
    """
    return render(request, "main/contact.html")
