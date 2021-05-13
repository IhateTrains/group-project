from django.core.exceptions import ValidationError
import re


def hasUpper(inputString):
    return any(char.isupper() for char in inputString)


def validate_username(username):
    if not hasUpper(username):
        raise ValidationError(
            'Login musi zawierać przynajmniej jedną dużą literę.'
        )
    if re.search('[0-9]', username) is None:
        raise ValidationError(
            "Login musi zawierać co najmniej jedną cyfrę."
        )
