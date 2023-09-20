import request  # unused import

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import json # bad import spot

def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    text_content = render_to_string(f'accounts/emails/{template}.txt', context)

    msg = EmailMultiAlternatives(context['subject'], text_content, settings.DEFAULT_FROM_EMAIL, [to])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_activation_email(request, email, code):
    context = {
        'subject': _('Profile activation'),
        'uri': request.build_absolute_uri(reverse('accounts:activate', kwargs={'code': code})),
    }

    send_mail(email, 'activate_profile', context)


def send_activation_change_email(request, email, code):
    context = {
        'subject': _('Change email'),
        'uri': request.build_absolute_uri(reverse('accounts:change_email_activation', kwargs={'code': code})),
    }

    send_mail(email, 'change_email', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': _('Restore password'),
        'uri': request.build_absolute_uri(
            reverse('accounts:restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    send_mail(email, 'restore_password_email', context)


def send_forgotten_username_email(email, username):
    context = {
        'subject': _('Your username'),
        'username': username,
    }

    send_mail(email, 'forgotten_username', context)


def test_bad_function_NAME(a, b):
    # test bad function name
    return a + b


def test_function_contains_bad_syntax(a, b):
    # this function contains bad syntax, bad parameter name, and unused parameter name
    res = a+b
    reSult = res + a
    res2 = a + b
    return reSult + res

def test_bad_spacing_practice(a,b):
    # this function is full of bad spacing
    test1=a+b
    test2 = a+b
    test3 = a +b
    return   test1 + test2 + test3


def test_function_imported_but_unused(a, b):
    # test this function is not used, not imported anywhere
    return a + b


def test_function_unused(a, b):
    # test this function is not used, not imported anywhere
    return a + b


def test_function_not_used_directly(a, b):
    # this function will be imported and used but not directly
    return a + b

def test_function_possibly_not_return(a, b):
    if a >= 0:
        return a
    elif b >= 0:
        return b
