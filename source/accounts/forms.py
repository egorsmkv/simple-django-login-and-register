from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.forms import (
    BooleanField,
    CharField,
    EmailField,
    Form,
    PasswordInput,
    ValidationError,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Activation, User


class UserCacheMixin:
    user_cache: User | None = None


class SignIn(UserCacheMixin, Form):
    password = CharField(label=_("Password"), strip=False, widget=PasswordInput)

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ["username", "password", "remember_me"]
        return ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.USE_REMEMBER_ME:
            self.fields["remember_me"] = BooleanField(
                label=_("Remember me"), required=False
            )

    def clean_password(self):
        password = self.cleaned_data["password"]

        if not self.user_cache:
            return password

        if not self.user_cache.check_password(password):
            raise ValidationError(_("You entered an invalid password."))

        return password


class SignInViaUsernameForm(SignIn):
    username = CharField(label=_("Username"))

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ["username", "password", "remember_me"]
        return ["username", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]

        user: User | None = User.objects.filter(username=username).first()
        if not user:
            raise ValidationError(_("You entered an invalid username."))

        if not user.is_active:
            raise ValidationError(_("This account is not active."))

        self.user_cache = user

        return username


class EmailForm(UserCacheMixin, Form):
    email = EmailField(label=_("Email"))

    def clean_email(self):
        email = self.cleaned_data["email"]

        user: User | None = User.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_("You entered an invalid email address."))

        if not user.is_active:
            raise ValidationError(_("This account is not active."))

        self.user_cache = user

        return email


class SignInViaEmailForm(SignIn, EmailForm):
    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ["email", "password", "remember_me"]
        return ["email", "password"]


class EmailOrUsernameForm(UserCacheMixin, Form):
    email_or_username = CharField(label=_("Email or Username"))

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data["email_or_username"]

        user: User | None = User.objects.filter(
            Q(username=email_or_username) | Q(email__iexact=email_or_username)
        ).first()
        if not user:
            raise ValidationError(
                _("You entered an invalid email address or username.")
            )

        if not user.is_active:
            raise ValidationError(_("This account is not active."))

        self.user_cache = user

        return email_or_username


class SignInViaEmailOrUsernameForm(SignIn, EmailOrUsernameForm):
    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ["email_or_username", "password", "remember_me"]
        return ["email_or_username", "password"]


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = settings.SIGN_UP_FIELDS

    email = EmailField(
        label=_("Email"), help_text=_("Required. Enter an existing email address.")
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        user = User.objects.filter(email__iexact=email).exists()
        if user:
            raise ValidationError(_("You can not use this email address."))

        return email


class ResendActivationCodeForm(UserCacheMixin, Form):
    email_or_username = CharField(label=_("Email or Username"))

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data["email_or_username"]

        user: User | None = User.objects.filter(
            Q(username=email_or_username) | Q(email__iexact=email_or_username)
        ).first()
        if not user:
            raise ValidationError(
                _("You entered an invalid email address or username.")
            )

        if user.is_active:
            raise ValidationError(_("This account has already been activated."))

        activation: Activation | None = Activation.objects.filter(user=user).first()
        if not activation:
            raise ValidationError(_("Activation code not found."))

        created_at: datetime = activation.created_at
        now_with_shift = timezone.now() - timedelta(hours=24)
        if created_at > now_with_shift:
            raise ValidationError(
                _(
                    "Activation code has already been sent. You can request a new code in 24 hours."
                )
            )

        self.user_cache = user

        return email_or_username


class ResendActivationCodeViaEmailForm(UserCacheMixin, Form):
    email = EmailField(label=_("Email"))

    def clean_email(self):
        email = self.cleaned_data["email"]

        user: User | None = User.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_("You entered an invalid email address."))

        if user.is_active:
            raise ValidationError(_("This account has already been activated."))

        activation: Activation | None = Activation.objects.filter(user=user).first()
        if not activation:
            raise ValidationError(_("Activation code not found."))

        created_at: datetime = activation.created_at
        now_with_shift = timezone.now() - timedelta(hours=24)
        if created_at > now_with_shift:
            raise ValidationError(
                _(
                    "Activation code has already been sent. You can request a new code in 24 hours."
                )
            )

        self.user_cache = user

        return email


class RestorePasswordForm(EmailForm):
    pass


class RestorePasswordViaEmailOrUsernameForm(EmailOrUsernameForm):
    pass


class ChangeProfileForm(Form):
    first_name = CharField(label=_("First name"), max_length=30, required=False)
    last_name = CharField(label=_("Last name"), max_length=150, required=False)


class ChangeEmailForm(Form):
    email = EmailField(label=_("Email"))

    def __init__(self, user, **kwargs):
        self.user = user
        super().__init__(**kwargs)  # pyrefly: ignore

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email == self.user.email:
            raise ValidationError(_("Please enter another email."))

        user = User.objects.filter(
            Q(email__iexact=email) & ~Q(id=self.user.id)
        ).exists()
        if user:
            raise ValidationError(_("You can not use this mail."))

        return email


class RemindUsernameForm(EmailForm):
    pass
