from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    UniqueConstraint,
)
from rest_framework.exceptions import ValidationError


class MyUser(AbstractUser):
    """
    Модель пользователя.
    Все поля обязательные.
    """
    first_name = CharField(
        'Имя',
        max_length=150
    )
    last_name = CharField(
        'Фамилия',
        max_length=150
    )
    email = EmailField(
        'Email',
        unique=True,
        max_length=200
    )
    is_subscribed = BooleanField(
        'Подписан',
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Follow(Model):
    """
    Модель подписок на авторов.
    Подписаться на себя нельзя.
    """
    user = ForeignKey(
        MyUser,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=CASCADE
    )
    author = ForeignKey(
        MyUser,
        related_name='followings',
        verbose_name='Автор',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower'
            )
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                {'error': 'Нельзя подписаться на себя'}
            )

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'
