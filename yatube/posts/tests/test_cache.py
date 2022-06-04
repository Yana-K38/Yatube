from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cach_index(self):
        """Проверка кеширования для index."""
        response = self.guest_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='Новый пост',
            author=self.user,
        )
        response_2 = self.guest_client.get(reverse('posts:index')).content
        self.assertEqual(response_2, response)
        cache.clear()
        response_3 = self.guest_client.get(reverse('posts:index')).content
        self.assertNotEqual(response_2, response_3)
