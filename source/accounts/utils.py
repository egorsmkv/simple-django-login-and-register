from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignInViaEmailForm


def get_login_form():
    if hasattr(settings, 'LOGIN_VIA_EMAIL') and settings.LOGIN_VIA_EMAIL:
        return SignInViaEmailForm

    return AuthenticationForm
