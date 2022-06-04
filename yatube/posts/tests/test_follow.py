from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='follower')
        cls.user_2 = User.objects.create_user(username='unfollower')
        cls.author = User.objects.create_user(username='following')
        cls.post = Post.objects.create(
            text='Тест подписчик',
            author=cls.author
        )

    def setUp(self):
        self.follower = Client()
        self.follower.force_login(self.user)
        self.unfollower = Client()
        self.unfollower.force_login(self.user_2)
        self.following = Client()
        self.following.force_login(self.author)

    def test_follow(self):
        """Проверка, что пост автора отобразится только у подписчика."""
        self.follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        form_data = {'text': 'Проверка подписки', }
        self.following.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertContains(response, form_data['text'])
        response = self.unfollower.get(reverse('posts:follow_index'))
        self.assertNotContains(response, form_data['text'])

    def test_follow_authorized_client(self):
        """Авторизованный пользователь может подписываться
        на других пользователей."""
        self.follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_authorized_client(self):
        self.follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.author}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)
