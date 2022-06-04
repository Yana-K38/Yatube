from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.field_verboses = [
            ('text', 'Текст поста', (cls.post)),
            ('author', 'Автор поста', (cls.post)),
            ('title', 'Название группы', (cls.group)),
            ('slug', 'URL', (cls.group)),
            ('description', 'Описание группы', (cls.group)),
        ]
        cls.field_help_texts = [
            ('title', 'Введите название группы', (cls.group)),
            ('description', 'Напишите описание группы', (cls.group)),
            ('text', 'Введите текст поста', (cls.post)),
        ]

    def test_label(self):
        """verbose_name поля совпадает с ожидаемым."""
        for field, expected_value, model in PostModelTest.field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_test(self):
        """help_text поля совпадает с ожидаемым."""
        for field, expected_value, model in PostModelTest.field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).help_text,
                    expected_value)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        posts = PostModelTest.post
        self.assertEqual(group.title, str(self.group))
        self.assertEqual(posts.text[:15], str(self.post))
