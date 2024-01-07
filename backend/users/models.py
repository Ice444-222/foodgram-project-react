from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_username


class UserRoles(models.TextChoices):
    ADMIN = "admin"
    USER = "user"


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+\Z",
                "В никнейме допустимы только цифры, буквы и символы @/./+/-/_",
            ),
            validate_username,
        ],
        verbose_name="Никнейм",
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Электронная почта",
    )
    first_name = models.CharField(
        max_length=150, verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=150, verbose_name="Фамилия",
    )
    role = models.CharField(
        choices=UserRoles.choices,
        default=UserRoles.USER,
        max_length=20,
        verbose_name="Роль",
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscription = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'], name='subscriptions_unique')]
