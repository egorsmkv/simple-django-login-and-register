from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

from .models import Activation
from .forms import SignInViaEmailForm, SignInViaEmailOrForm, PasswordResetViaEmailOrUsernameForm


def get_login_form():
    if hasattr(settings, 'LOGIN_VIA_EMAIL') and settings.LOGIN_VIA_EMAIL:
        return SignInViaEmailForm

    if hasattr(settings, 'LOGIN_VIA_EMAIL_OR_USERNAME') and settings.LOGIN_VIA_EMAIL_OR_USERNAME:
        return SignInViaEmailOrForm

    return AuthenticationForm


def get_password_reset_form():
    if hasattr(settings, 'PASSWORD_RESET_VIA_EMAIL_OR_USERNAME') and settings.PASSWORD_RESET_VIA_EMAIL_OR_USERNAME:
        return PasswordResetViaEmailOrUsernameForm

    return PasswordResetForm


def send_activation_email(request, user):
    subject = 'Profile Activation'

    from_email = settings.DEFAULT_FROM_EMAIL
    domain = Site.objects.get_current().domain
    code = get_random_string(20)

    context = {
        'domain': domain,
        'code': code,
    }

    act = Activation()
    act.code = code
    act.user = user
    act.save()

    html_content = render_to_string('email/activation_profile.html', context=context, request=request)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
