from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .models import Activation


def send_activation_email(request, user):
    code = get_random_string(20)

    act = Activation()
    act.code = code
    act.user = user
    act.save()

    subject = _('Profile activation')
    context = {
        'subject': subject,
        'uri': request.build_absolute_uri(reverse('accounts:activate', kwargs={'code': code})),
    }

    html_content = render_to_string('accounts/email/activate_profile.html', context)
    text_content = render_to_string('accounts/email/activate_profile.txt', context)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_activation_change_email(request, user, new_email):
    code = get_random_string(20)

    act = Activation()
    act.code = code
    act.user = user
    act.email = new_email
    act.save()

    subject = _('Change email')
    context = {
        'subject': subject,
        'uri': request.build_absolute_uri(reverse('accounts:change_email_activation', kwargs={'code': code})),
    }

    html_content = render_to_string('accounts/email/change_email.html', context)
    text_content = render_to_string('accounts/email/change_email.txt', context)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_reset_password_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()

    subject = _('Restore password')
    context = {
        'subject': subject,
        'uri': request.build_absolute_uri(
            reverse('accounts:restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    html_content = render_to_string('accounts/email/restore_password_email.html', context)
    text_content = render_to_string('accounts/email/restore_password_email.txt', context)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_forgotten_username(email):
    user = User.objects.filter(email=email).first()

    subject = _('Your username')
    context = {
        'subject': subject,
        'username': user.username,
    }

    html_content = render_to_string('accounts/email/forgotten_username.html', context)
    text_content = render_to_string('accounts/email/forgotten_username.txt', context)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
