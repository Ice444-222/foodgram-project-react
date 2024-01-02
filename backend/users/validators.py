from django.core.exceptions import ValidationError


def validate_username(value):
    if value == "admin":
        raise ValidationError("Никнейм 'admin' не допустим.")
