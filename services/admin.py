from django.contrib import admin

from services.models import (Appointment, DiagnosisResult, DoctorSchedule,
                             Service, ServiceCategory)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "day_of_week",
    )
    list_filter = ("doctor",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "service",
        "doctor",
        "scheduled_at",
    )
    list_filter = ("scheduled_at",)


@admin.register(DiagnosisResult)
class DiagnosisResultAdmin(admin.ModelAdmin):
    list_display = (
        "appointment",
        "patient",
        "status",
    )
    list_filter = ("appointment",)
