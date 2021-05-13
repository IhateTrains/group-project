from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class MinimalLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Hasło musi zawierać co najmniej %(min_length)d znaków."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Hasło musi zawierać co najmniej %(min_length)d znaków."
            % {'min_length': self.min_length}
        )


class AtLeastOneDigitValidator:
    @staticmethod
    def validate(password, user=None):
        if re.search('[0-9]', password) is None:
            raise ValidationError(
                _("Hasło musi zawierać co najmniej jedną cyfrę."),
                code='does_not_contain_digit',
            )

    @staticmethod
    def get_help_text():
        return _(
            "Hasło musi zawierać co najmniej jedną cyfrę."
        )


def hasUpper(inputString):
    return any(char.isupper() for char in inputString)


class AtLeastOneUppercaseLetterValidator:
    @staticmethod
    def validate(password, user=None):
        if not hasUpper(password):
            raise ValidationError(
                _("Hasło musi zawierać co najmniej jedną dużą literę."),
                code='does_not_contain_uppercase_letter',
            )

    @staticmethod
    def get_help_text():
        return _(
            "Hasło musi zawierać co najmniej jedną dużą literę."
        )
