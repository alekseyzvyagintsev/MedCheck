from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.forms import UserProfileForm, UserRegistrationForm

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="testpass123"
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertEqual(admin_user.username, "admin")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class AccountsViewsTest(TestCase):
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

    def test_register_view_get(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_view_post(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "date_of_birth": "1990-01-01",
        }
        response = self.client.post(reverse("accounts:register"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_create_doctor_view_get(self):
        self.client.login(username="doctor", password="testpass123")
        response = self.client.get(reverse("accounts:create_doctor"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/create_doctor.html")

    def test_create_doctor_view_post(self):
        self.client.login(username="doctor", password="testpass123")
        form_data = {
            "username": "newdoctor",
            "email": "newdoctor@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "date_of_birth": "1980-01-01",
        }
        response = self.client.post(reverse("accounts:create_doctor"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(username="newdoctor", is_staff=True).exists()
        )

    def test_login_view(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_logout_view(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:home"))


class AccountsFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_registration_form_valid(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "date_of_birth": "1990-01-01",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form_invalid_phone(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "phone": "invalid_phone",
            "date_of_birth": "1990-01-01",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_user_profile_form_valid(self):
        form_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "date_of_birth": "1990-01-01",
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
