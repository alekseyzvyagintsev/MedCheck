from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("diagnosis-result/<int:appointment_id>/", views.diagnosis_result_detail, name="diagnosis_result_detail"),
    path("categories/", views.category_list, name="category-list"),
    path("services/", views.services, name="services"),
    path(
        "category/<int:category_id>/", views.category_services, name="category-services"
    ),
    path("services/<int:service_id>/", views.service_detail, name="service_detail"),
    # Страница формы записи на приём
    path("appointment/", views.get_services, name="get_services"),
    # Пошаговая запись на приём
    path("appointment/", views.get_services, name="get_services"),
    path("appointment/choose-service/", views.choose_service, name="choose_service"),
    path("appointment/choose-doctor/", views.choose_doctor, name="choose_doctor"),
    path("appointment/choose-date/", views.choose_date, name="choose_date"),
    path("appointment/confirm/", views.confirm_appointment, name="confirm_appointment"),
    # API для записей на приём
    path("api/appointments/", views.create_appointment, name="create-appointment"),
    path(
        "appointments/<int:appointment_id>/delete/",
        views.delete_appointment,
        name="delete-appointment",
    ),
    path(
        "api/appointments/available_slots/<int:doctor_id>/",
        views.get_available_slots,
        name="get-available-slots",
    ),
    path("dashboard/", views.doctor_dashboard, name="dashboard"),
    path("result/<int:appointment_id>/create/", views.create_diagnosis_result, name="create_result"),
    path("result/<int:appointment_id>/view/", views.view_diagnosis_result, name="view_result"),
    path("result/<int:appointment_id>/edit/", views.edit_diagnosis_result, name="edit_result"),
    path("result/<int:appointment_id>/delete/", views.delete_diagnosis_result, name="delete_result"),
]
