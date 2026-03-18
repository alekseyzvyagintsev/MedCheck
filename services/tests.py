from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from services.models import (Appointment, DiagnosisResult, DoctorSchedule,
                             Service, ServiceCategory)
from services.utils.appointments import (create_appointment_logic,
                                         delete_appointment_logic,
                                         parse_datetime_string,
                                         validate_appointment_time)
from services.utils.diagnostic_results import (create_diagnostic_result,
                                               update_diagnostic_result)
from services.utils.doctors import create_doctor_schedule

User = get_user_model()


class ServiceModelTest(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name="Тестовая категория", description="Описание тестовой категории"
        )
        self.doctor = User.objects.create_user(
            username="doctor", email="doctor@example.com", password="testpass123"
        )

    def test_create_service_category(self):
        self.assertEqual(str(self.category), "Тестовая категория")
        self.assertTrue(self.category.is_active)

    def test_create_service(self):
        service = Service.objects.create(
            name="Тестовая услуга",
            category=self.category,
            description="Описание услуги",
            short_description="Краткое описание",
            price=1000.00,
            duration=30,
        )
        self.assertEqual(str(service), "Тестовая услуга (Тестовая категория)")
        self.assertEqual(service.price_formatted, "1 000")

    def test_doctor_schedule(self):
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor, day_of_week=0, time_of_day=0  # Понедельник  # 09:00
        )
        self.assertEqual(str(schedule), f"{self.doctor} - Понедельник: 09:00")
        self.assertTrue(schedule.is_active)

    def test_appointment_creation(self):
        service = Service.objects.create(
            name="Тестовая услуга",
            category=self.category,
            description="Описание услуги",
            short_description="Краткое описание",
            price=1000.00,
            duration=30,
        )
        appointment = Appointment.objects.create(
            patient=self.doctor,
            service=service,
            doctor=self.doctor,
            scheduled_at=timezone.now(),
        )
        self.assertEqual(
            str(appointment),
            f"Запись: {self.doctor} к {self.doctor} на {appointment.scheduled_at}",
        )
        self.assertTrue(appointment.is_active)


class ServicesViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.staff_user = User.objects.create_user(
            username="doctor",
            email="doctor@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.category = ServiceCategory.objects.create(
            name="Тестовая категория", description="Описание тестовой категории"
        )
        self.service = Service.objects.create(
            name="Тестовая услуга",
            category=self.category,
            description="Описание услуги",
            short_description="Краткое описание",
            price=1000.00,
            duration=30,
        )
        self.service.doctors.add(self.staff_user)
        create_doctor_schedule(self.staff_user)

    def test_category_list_view(self):
        response = self.client.get(reverse("services:category_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/categories.html")
        self.assertIn("categories", response.context)

    def test_services_view(self):
        response = self.client.get(reverse("services:services"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/services.html")
        self.assertIn("services", response.context)

    def test_category_services_view(self):
        response = self.client.get(
            reverse(
                "services:category_services", kwargs={"category_id": self.category.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/services.html")
        self.assertIn("services", response.context)

    def test_service_detail_view(self):
        response = self.client.get(
            reverse("services:service_detail", kwargs={"service_id": self.service.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service_detail.html")
        self.assertIn("service", response.context)

    def test_get_services_step(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("services:get_services"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/steps/step1_choose_service.html")

    def test_choose_service(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("services:choose_service"), {"service_id": self.service.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/steps/step2_choose_doctor.html")
        self.assertIn("service", response.context)
        self.assertIn("doctors", response.context)

    def test_choose_doctor(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("services:choose_doctor"),
            {"doctor_id": self.staff_user.id, "service_id": self.service.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/steps/step3_choose_date.html")
        self.assertIn("doctor", response.context)
        self.assertIn("service", response.context)

    def test_choose_date(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("services:choose_date"),
            {
                "doctor_id": self.staff_user.id,
                "service_id": self.service.id,
                "date": timezone.now().date().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/steps/step4_choose_time.html")
        self.assertIn("doctor", response.context)
        self.assertIn("service", response.context)
        self.assertIn("date", response.context)
        self.assertIn("slots", response.context)

    def test_confirm_appointment(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("services:confirm_appointment"),
            {
                "service_id": self.service.id,
                "doctor_id": self.staff_user.id,
                "scheduled_at": (timezone.now() + timezone.timedelta(days=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/steps/step5_confirmation.html")
        self.assertIn("appointment_id", response.context)

    def test_create_appointment(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("services:create_appointment"),
            data={
                "service_id": self.service.id,
                "doctor_id": self.staff_user.id,
                "scheduled_at": (timezone.now() + timezone.timedelta(days=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            },
            content_type="application/json",
        )
        # Для отладки
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_delete_appointment(self):
        self.client.login(username="testuser", password="testpass123")
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
        )
        response = self.client.post(
            reverse(
                "services:delete_appointment", kwargs={"appointment_id": appointment.id}
            )
        )
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertFalse(appointment.is_active)

    def test_get_available_slots(self):
        self.client.login(username="testuser", password="testpass123")
        future_date = timezone.now() + timezone.timedelta(days=1)
        response = self.client.get(
            reverse(
                "services:get_available_slots", kwargs={"doctor_id": self.staff_user.id}
            ),
            {"date": future_date.date().isoformat()},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("slots", response.json())

    def test_doctor_dashboard(self):
        self.client.login(username="doctor", password="testpass123")
        response = self.client.get(reverse("services:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/doctor/dashboard.html")
        self.assertIn("today_appointments", response.context)

    def test_create_diagnosis_result(self):
        self.client.login(username="doctor", password="testpass123")
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
        )
        response = self.client.get(
            reverse("services:create_result", kwargs={"appointment_id": appointment.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/doctor/result_form.html")

    def test_view_diagnosis_result(self):
        self.client.login(username="doctor", password="testpass123")
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
        )
        diagnosis_result = DiagnosisResult.objects.create(
            appointment=appointment, status="completed"
        )
        response = self.client.get(
            reverse("services:view_result", kwargs={"appointment_id": appointment.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/doctor/result_detail.html")
        self.assertIn("result", response.context)

    def test_edit_diagnosis_result(self):
        self.client.login(username="doctor", password="testpass123")
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
        )
        diagnosis_result = DiagnosisResult.objects.create(
            appointment=appointment, status="completed"
        )
        response = self.client.get(
            reverse("services:edit_result", kwargs={"appointment_id": appointment.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/doctor/result_form.html")
        self.assertIn("result", response.context)
        self.assertIn("appointment", response.context)
        self.assertIn("form", response.context)

    def test_delete_diagnosis_result(self):
        self.client.login(username="doctor", password="testpass123")
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
        )
        diagnosis_result = DiagnosisResult.objects.create(
            appointment=appointment, status="completed"
        )
        response = self.client.post(
            reverse("services:delete_result", kwargs={"appointment_id": appointment.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            DiagnosisResult.objects.filter(appointment=appointment).exists()
        )


class ServicesUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.staff_user = User.objects.create_user(
            username="doctor",
            email="doctor@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.category = ServiceCategory.objects.create(
            name="Тестовая категория", description="Описание тестовой категории"
        )
        self.service = Service.objects.create(
            name="Тестовая услуга",
            category=self.category,
            description="Описание услуги",
            short_description="Краткое описание",
            price=1000.00,
            duration=30,
        )
        self.service.doctors.add(self.staff_user)

    def test_parse_datetime_string(self):
        datetime_str = "2026-03-18 09:00:00"
        result = parse_datetime_string(datetime_str)
        self.assertEqual(result.strftime("%Y-%m-%d %H:%M:%S"), datetime_str)

    def test_validate_appointment_time_future(self):
        future_time = timezone.now() + timezone.timedelta(hours=1)
        result = validate_appointment_time(future_time)
        self.assertTrue(result)

    def test_validate_appointment_time_past(self):
        past_time = timezone.now() - timezone.timedelta(hours=1)
        with self.assertRaises(ValueError):
            validate_appointment_time(past_time)

    def test_create_appointment_logic_success(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        success, result = create_appointment_logic(
            patient=self.user,
            service_id=self.service.id,
            doctor_id=self.staff_user.id,
            scheduled_at=future_time,
        )
        self.assertTrue(success)
        self.assertIn("appointment_id", result)

    def test_create_appointment_logic_past_time(self):
        past_time = timezone.now() - timezone.timedelta(hours=1)
        success, result = create_appointment_logic(
            patient=self.user,
            service_id=self.service.id,
            doctor_id=self.staff_user.id,
            scheduled_at=past_time,
        )
        self.assertFalse(success)
        self.assertIn("error", result)

    def test_create_appointment_logic_invalid_service(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        success, result = create_appointment_logic(
            patient=self.user,
            service_id=999,
            doctor_id=self.staff_user.id,
            scheduled_at=future_time,
        )
        self.assertFalse(success)
        self.assertIn("error", result)

    def test_delete_appointment_logic_success(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        success, result = delete_appointment_logic(
            appointment_id=appointment.id, user=self.user
        )
        self.assertTrue(success)
        appointment.refresh_from_db()
        self.assertFalse(appointment.is_active)

    def test_delete_appointment_logic_not_found(self):
        success, result = delete_appointment_logic(appointment_id=999, user=self.user)
        self.assertFalse(success)
        self.assertIn("error", result)

    def test_delete_appointment_logic_no_permission(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        success, result = delete_appointment_logic(
            appointment_id=appointment.id, user=other_user
        )
        self.assertFalse(success)
        self.assertIn("error", result)

    def test_create_diagnostic_result(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        result = create_diagnostic_result(appointment)
        self.assertEqual(result.appointment, appointment)
        self.assertEqual(result.status, "processing")

    def test_update_diagnostic_result_with_files(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        # Создаем тестовый файл
        test_file = SimpleUploadedFile(
            "test_result.pdf", b"test content", content_type="application/pdf"
        )
        result = update_diagnostic_result(
            appointment=appointment, files=[test_file], description="Test description"
        )
        self.assertTrue(result["success"])
        diagnostic_result = DiagnosisResult.objects.get(appointment=appointment)
        self.assertEqual(diagnostic_result.status, "completed")
        self.assertEqual(diagnostic_result.description, "Test description")
        self.assertTrue(diagnostic_result.file)

    def test_update_diagnostic_result_with_description(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        result = update_diagnostic_result(
            appointment=appointment, description="Test description"
        )
        self.assertTrue(result["success"])
        diagnostic_result = DiagnosisResult.objects.get(appointment=appointment)
        self.assertEqual(diagnostic_result.status, "completed")
        self.assertEqual(diagnostic_result.description, "Test description")

    def test_update_diagnostic_result_no_data(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.user,
            service=self.service,
            doctor=self.staff_user,
            scheduled_at=future_time,
        )
        result = update_diagnostic_result(appointment=appointment)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
