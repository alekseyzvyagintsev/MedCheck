from django.shortcuts import render

from content.content import get_common_context
from services.models import ServiceCategory


def home(request):
    """
    Главная страница
    """
    categories = ServiceCategory.objects.all()

    context = get_common_context()
    context = {
        **context,
        "categories": categories,
        "category_list_url": "services:category_list",
    }

    return render(
        request,
        "main/home.html",
        context,
    )


def about(request):
    """
    Страница "О компании"
    """
    context = get_common_context()
    return render(
        request,
        "main/about.html",
        context,
    )


def contact(request):
    """
    Страница контактов
    """
    context = get_common_context()
    return render(
        request,
        "main/contact.html",
        context,
    )
