from datetime import timedelta

from django import forms
from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


def get_sign_up_fields():
    if settings.DISABLE_USERNAME:
        return ['first_name', 'last_name', 'email', 'password1', 'password2']

    return ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SignIn(forms.Form):
    password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput)
    user_cache = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.USE_REMEMBER_ME:
            self.fields['remember_me'] = forms.BooleanField(label=_('Remember me'), required=False)

    def clean_password(self):
        password = self.cleaned_data['password']

        if not self.user_cache:
            return password

        if not self.user_cache.check_password(password):
            raise ValidationError(_('You entered an invalid password.'))

        return password


class SignInViaUsernameForm(SignIn):
    username = forms.CharField(label=_('Username'))

    error_messages = {
        'invalid_username': _('You entered an invalid username.'),
        'inactive': _('This account is not active.'),
    }

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['username', 'password', 'remember_me']
        return ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']

        user = User.objects.filter(username=username).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_username'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return username


class SignInViaEmailForm(SignIn):
    email = forms.EmailField(label=_('Email'))

    error_messages = {
        'invalid_email': _('You entered an invalid email address.'),
        'inactive': _('This account is not active.'),
    }

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['email', 'password', 'remember_me']
        return ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return email


class SignInViaEmailOrUsernameForm(SignIn):
    email_or_username = forms.CharField(label=_('Email or Username'))

    error_messages = {
        'invalid_email_or_username': _('You entered an invalid email address or username.'),
        'inactive': _('This account is not active.'),
    }

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['email_or_username', 'password', 'remember_me']
        return ['email_or_username', 'password']

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        username = email_or_username
        email = email_or_username.lower()

        user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email_or_username'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return email_or_username


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = get_sign_up_fields()

    email = forms.EmailField(label=_('Email'), help_text=_('Required. Enter an existing email address.'))

    error_messages = {
        'unique_email': _('You can not use this email address.'),
    }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError(self.error_messages['unique_email'])

        return email


class ResendActivationCodeForm(forms.Form):
    email_or_username = forms.CharField(label=_('Email or Username'))

    user_cache = None
    error_messages = {
        'non_expired': _('Activation code has already been sent. You can request a new code in 24 hours.'),
        'invalid_email_or_username': _('You entered an invalid email address or username.'),
        'invalid_activation': _('Activation code not found.'),
        'already_activated': _('This account has already been activated.'),
    }

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        username = email_or_username
        email = email_or_username.lower()

        user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email_or_username'])

        if user.is_active:
            raise ValidationError(self.error_messages['already_activated'])

        now_with_shift = timezone.now() - timedelta(hours=24)
        activation = user.activation_set.first()
        if not activation:
            raise ValidationError(self.error_messages['invalid_activation'])

        if activation.created_at > now_with_shift:
            raise ValidationError(self.error_messages['non_expired'])

        self.user_cache = user

        return email_or_username


class ResendActivationCodeViaEmailForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    user_cache = None
    error_messages = {
        'non_expired': _('Activation code has already been sent. You can request a new code in 24 hours.'),
        'invalid_activation': _('Activation code not found.'),
        'invalid_email': _('You entered an invalid email address.'),
        'already_activated': _('This account has already been activated.'),
    }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email'])

        if user.is_active:
            raise ValidationError(self.error_messages['already_activated'])

        now_with_shift = timezone.now() - timedelta(hours=24)
        activation = user.activation_set.first()
        if not activation:
            raise ValidationError(self.error_messages['invalid_activation'])

        if activation.created_at > now_with_shift:
            raise ValidationError(self.error_messages['non_expired'])

        self.user_cache = user

        return email


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    user_cache = None
    error_messages = {
        'invalid_email': _('You entered an invalid email address.'),
        'inactive': _('This account is not active.'),
    }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return email


class RestorePasswordViaEmailOrUsernameForm(forms.Form):
    email_or_username = forms.CharField(label=_('Email or Username'))

    user_cache = None
    error_messages = {
        'invalid_email_or_username': _('You entered an invalid email address or username.'),
        'inactive': _('This account is not active.'),
    }

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        username = email_or_username
        email = email_or_username.lower()

        user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email_or_username'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return email_or_username


class ChangeProfileForm(forms.Form):
    first_name = forms.CharField(label=_('First name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('Last name'), max_length=150, required=False)


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    error_messages = {
        'email_already_exists': _('You can not use this mail.'),
        'same_email': _('Please enter another email.'),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if email == self.user.email:
            raise ValidationError(self.error_messages['same_email'])

        user = User.objects.filter(Q(email=email) & ~Q(id=self.user.id)).exists()
        if user:
            raise ValidationError(self.error_messages['email_already_exists'])

        return email


class RemindUsernameForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    user_cache = None
    error_messages = {
        'invalid_email': _('You entered an invalid email address.'),
        'inactive': _('This account is not active.'),
    }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError(self.error_messages['invalid_email'])

        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'])

        self.user_cache = user

        return email
