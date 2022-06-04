from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_all_user_urls(self):
        """Страницы доступны любому пользователю."""
        templates_url_names = (
            '/about/author/',
            '/about/tech/',
        )
        for urls in templates_url_names:
            response = self.guest_client.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
