from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('categories/', views.category_list, name='category-list'),
    path('services/', views.services, name='services'),
    path('category/<int:category_id>/', views.category_services, name='category-services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
]