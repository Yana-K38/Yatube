from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.client = User.objects.create_user(username='NoAuthor')
        cls.group = Group.objects.create(
            title='Звголовок тестовой группы',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.templates_url_names_html = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/404/': 'core/404.html'
        }
        cls.url_names = (
            '/',
            '/group/test_slug/',
            '/profile/auth/',
            '/posts/1/',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostURLTests.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.client)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL используют правильные шаблоны."""
        for url, template in PostURLTests.templates_url_names_html.items():
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)

    def test_all_user_all_page(self):
        for url in PostURLTests.url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.authorized_client.get('/posts/1/edit/')
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                response = self.guest_client.get('/posts/1/edit/')
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                response = self.guest_client.get('/create/')
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                response = self.author.get('/create/')
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.authorized_client.get('/create/')
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_url(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
