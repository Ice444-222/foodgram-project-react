from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_username


class UserRoles(models.TextChoices):
    ADMIN = "admin"
    USER = "user"


class User(AbstractUser):
    username = models.CharField(
        verbose_name="Никнейм",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+\Z",
                "В никнейме допустимы только цифры, буквы и символы @/./+/-/_",
            ),
            validate_username,
        ],
    )
    email = models.EmailField(
        verbose_name="Электронная почта", max_length=254, unique=True
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=150,
    )
    role = models.CharField(
        verbose_name="Роль",
        choices=UserRoles.choices,
        default=UserRoles.USER,
        max_length=20,
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
