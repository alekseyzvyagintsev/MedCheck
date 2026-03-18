from django.test import TestCase
from django.urls import reverse


class MainViewsTest(TestCase):
    def test_home_view(self):
        """
        Проверка главной страницы
        """
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/home.html")

    def test_about_view(self):
        """
        Проверка страницы "О компании"
        """
        response = self.client.get(reverse("main:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/about.html")

    def test_contact_view(self):
        """
        Проверка страницы контактов
        """
        response = self.client.get(reverse("main:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/contact.html")
