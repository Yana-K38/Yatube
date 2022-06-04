from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorTest(TestCase):
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
        cls.pages_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.bulk_create(
            [
                Post(
                    author=PaginatorTest.user,
                    text=post,
                    group=PaginatorTest.group)
                for post in range(12)
            ],
        )

    def test_first_page(self):
        for reverse_name in PaginatorTest.pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page(self):
        for reverse_name in PaginatorTest.pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name, {'page': 2})
                self.assertEqual(len(response.context['page_obj']), 3)
