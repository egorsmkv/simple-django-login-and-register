from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .models import Activation
from .forms import (
    SignInViaEmailForm, SignInViaEmailOrUsernameForm, PasswordResetViaEmailOrUsernameForm,
    ReSendActivationCodeForm, ReSendActivationCodeViaEmailForm
)


def get_login_form():
    if hasattr(settings, 'LOGIN_VIA_EMAIL') and settings.LOGIN_VIA_EMAIL:
        return SignInViaEmailForm

    if hasattr(settings, 'LOGIN_VIA_EMAIL_OR_USERNAME') and settings.LOGIN_VIA_EMAIL_OR_USERNAME:
        return SignInViaEmailOrUsernameForm

    return AuthenticationForm


def is_username_disabled():
    return hasattr(settings, 'DISABLE_USERNAME') and settings.DISABLE_USERNAME


def get_password_reset_form():
    if is_username_disabled():
        return PasswordResetForm

    if hasattr(settings, 'PASSWORD_RESET_VIA_EMAIL_OR_USERNAME') and settings.PASSWORD_RESET_VIA_EMAIL_OR_USERNAME:
        return PasswordResetViaEmailOrUsernameForm

    return PasswordResetForm


def get_resend_ac_form():
    if is_username_disabled():
        return ReSendActivationCodeViaEmailForm

    return ReSendActivationCodeForm


def send_activation_email(request, user):
    subject = _('Profile Activation')

    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    domain = current_site.domain
    code = get_random_string(20)

    context = {
        'domain': domain,
        'code': code,
    }

    act = Activation()
    act.code = code
    act.user = user
    act.save()

    html_content = render_to_string('accounts/email/activation_profile.html', context=context, request=request)
    text_content = render_to_string('accounts/email/activation_profile.txt', context=context, request=request)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_activation_change_email(request, user, new_email):
    subject = _('Change email')

    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    domain = current_site.domain
    code = get_random_string(20)

    context = {
        'domain': domain,
        'code': code,
    }

    act = Activation()
    act.code = code
    act.user = user
    act.email = new_email
    act.save()

    html_content = render_to_string('accounts/email/change_email.html', context=context, request=request)
    text_content = render_to_string('accounts/email/change_email.txt', context=context, request=request)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_reset_password_email(request, user):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain

    token_generator = default_token_generator
    use_https = request.is_secure()

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'user': user,
        'token': token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
    }

    subject = render_to_string('registration/password_reset_subject.txt', context)
    subject = ''.join(subject.splitlines())
    body = render_to_string('registration/password_reset_email.html', context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [user.email])
    email_message.send()
