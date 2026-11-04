from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Токен для подтверждения email."""

    def _make_hash_value(self, user, timestamp):
        # Хэш: user.pk + timestamp + is_email_verified
        return f'{user.pk}{timestamp}{user.is_email_verified}'


email_verification_token = EmailVerificationTokenGenerator()
