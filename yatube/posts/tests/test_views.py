import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)


class PostViewsTests(TestCase):
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
            image=SimpleUploadedFile(
                name="small.gif",
                content=SMALL_GIF,
                content_type="image/gif"
            )
        )
        cls.template_pag_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
        }
        cls.urls_name = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'auth'}),
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}))

    def setUp(self):
        self.client = User.objects.create_user(username='NoAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.client)
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostViewsTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in PostViewsTests.template_pag_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'], Page)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': 'test_slug'}))
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        post_author_0 = first_object.author
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        image_0 = first_object.image
        self.assertEqual(
            group_title_0,
            PostViewsTests.group.title
        )
        self.assertEqual(
            post_author_0,
            PostViewsTests.user
        )
        self.assertEqual(
            group_description_0,
            PostViewsTests.group.description
        )
        self.assertEqual(
            group_slug_0,
            PostViewsTests.group.slug
        )
        self.assertEqual(
            image_0,
            PostViewsTests.post.image
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_post_0 = first_object.text
        post_id_0 = first_object.id
        post_img_0 = first_object.image
        self.assertEqual(post_post_0, PostViewsTests.post.text)
        self.assertEqual(post_author_0, PostViewsTests.user)
        self.assertEqual(post_id_0, PostViewsTests.post.id)
        self.assertEqual(post_img_0, PostViewsTests.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(
            response.context['post'].text,
            PostViewsTests.post.text
        )
        self.assertEqual(
            response.context['post'].author,
            PostViewsTests.user
        )
        self.assertEqual(
            response.context['post'].group,
            PostViewsTests.group
        )
        self.assertEqual(
            response.context['post'].image,
            PostViewsTests.post.image
        )

    def test_create_edit_show_correct_context(self):
        """Шаблон post_create, post_edit сформирован
        с правильным контекстом."""
        response = self.author.get(reverse('posts:post_create'))
        response_edit = self.author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                form_field_edit = response_edit.context.get(
                    'form', 'is_edit').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(form_field_edit, expected)

    def test_create(self):
        """Появиться пост на страницах index, profile, group_list"""
        post_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый текст',
                'group': 'Тестовая группа',
                'image': PostViewsTests.post.image
            }
        )
        for url in PostViewsTests.urls_name:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
            if PostViewsTests.group is True:
                self.assertEqual(Post.objects.count(), post_count + 1)
                self.assertEqual(
                    response.context['post'].text,
                    PostViewsTests.post.text)
                self.assertEqual(
                    response.context['post'].group,
                    PostViewsTests.group)
                self.assertEqual(
                    response.context['post'].image,
                    PostViewsTests.post.image)
