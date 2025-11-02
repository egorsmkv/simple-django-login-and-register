from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import string
import secrets
from random import SystemRandom

def send_mail(to, template, context):
    html_content = render_to_string(f"accounts/emails/{template}.html", context)
    text_content = render_to_string(f"accounts/emails/{template}.txt", context)

    msg = EmailMultiAlternatives(
        context["subject"], text_content, settings.DEFAULT_FROM_EMAIL, [to]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_activation_email(request, email, code):
    context = {
        "subject": _("Profile activation"),
        "uri": request.build_absolute_uri(
            reverse("accounts:activate", kwargs={"code": code})
        ),
    }

    send_mail(email, "activate_profile", context)


def send_activation_change_email(request, email, code):
    context = {
        "subject": _("Change email"),
        "uri": request.build_absolute_uri(
            reverse("accounts:change_email_activation", kwargs={"code": code})
        ),
    }

    send_mail(email, "change_email", context)


def send_reset_password_email(request, email, token, uid):
    context = {
        "subject": _("Restore password"),
        "uri": request.build_absolute_uri(
            reverse(
                "accounts:restore_password_confirm",
                kwargs={"uidb64": uid, "token": token},
            )
        ),
    }

    send_mail(email, "restore_password_email", context)


def send_forgotten_username_email(email, username):
    context = {
        "subject": _("Your username"),
        "username": username,
    }

    send_mail(email, "forgotten_username", context)

_sysrand = SystemRandom()
def generate_secure_password(length: int = 20,
                             use_lower: bool = True,
                             use_upper: bool = True,
                             use_digits: bool = True,
                             use_symbols: bool = True,
                             require_each: bool = True) -> str:

    """
    Generate a cryptographically secure random password.

    Parameters:
        length (int): Length of the password (default 20)
        use_lower (bool): Include lowercase letters
        use_upper (bool): Include uppercase letters
        use_digits (bool): Include digits
        use_symbols (bool): Include symbols/punctuation
        require_each (bool): Ensure at least one character from each selected category is present

    Returns:
        str: Generated password
    """
    #Ensure positive length
    if length <= 0:
        raise ValueError("length must be > 0")

    #Collect selected character categories
    categories = []
    if use_lower:
        categories.append(string.ascii_lowercase)
    if use_upper:
        categories.append(string.ascii_uppercase)
    if use_digits:
        categories.append(string.digits)
    if use_symbols:
        symbols = string.punctuation
        categories.append(symbols)

    #Raise error if no category is selected
    if not categories:
        raise ValueError("At least one character category must be enabled")

    #Ensure length is sufficient if requiring one char from each category
    if require_each and length < len(categories):
        raise ValueError(f"length must be at least {len(categories)} when require_each=True")

    pool = "".join(categories)

    pw_chars = []

    #If require_each is True, pick one character from each category
    if require_each:
        for cat in categories:
            pw_chars.append(secrets.choice(cat))

    #Fill the remaining characters randomly from the pool
    remaining = length - len(pw_chars)
    for _ in range(remaining):
        pw_chars.append(secrets.choice(pool))

    #Shuffle the resulting password list to avoid predictable positions
    _sysrand.shuffle(pw_chars)

    return "".join(pw_chars)

