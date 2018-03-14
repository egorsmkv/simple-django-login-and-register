from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Activation

UserModel = get_user_model()


def get_sign_up_fields():
    if hasattr(settings, 'DISABLE_USERNAME') and settings.DISABLE_USERNAME:
        return ['first_name', 'last_name', 'email', 'password1', 'password2']

    return ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SignIn(forms.Form):
    redirect_field_name = REDIRECT_FIELD_NAME

    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def get_user(self):
        return self.user_cache


class SignInViaEmailForm(SignIn):
    field_order = ['email', 'password']

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': '@', 'autofocus': True}),
    )

    error_messages = {
        'invalid_login': _('Please enter a correct email and password. Note that both fields may be case-sensitive.'),
        'inactive': _('This account is inactive.'),
    }

    def clean(self):
        cleaned_data = super(SignInViaEmailForm, self).clean()

        email = cleaned_data.get('email', '').lower()
        password = cleaned_data.get('password', '')

        self.user_cache = UserModel.objects.filter(email=email).first()
        if self.user_cache:
            if not self.user_cache.is_active:
                self.add_error('email', self.error_messages['inactive'])

            if not self.user_cache.check_password(password):
                self.add_error('email', self.error_messages['invalid_login'])
        else:
            self.add_error('email', self.error_messages['invalid_login'])


class SignInViaEmailOrUsernameForm(SignIn):
    field_order = ['email_or_username', 'password']

    email_or_username = forms.CharField(
        label=_('Email or Username'),
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    error_messages = {
        'invalid_login': _(
            'Please enter a correct email or username and password. Note that both fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SignInViaEmailOrUsernameForm, self).clean()

        email_or_username = cleaned_data.get('email_or_username', '')
        password = cleaned_data.get('password', '')

        email = email_or_username.lower()
        username = email_or_username

        self.user_cache = UserModel.objects.filter(
            Q(username=username) | Q(email=email)
        ).first()

        if self.user_cache:
            if not self.user_cache.is_active:
                self.add_error('email_or_username', self.error_messages['inactive'])

            if not self.user_cache.check_password(password):
                self.add_error('email_or_username', self.error_messages['invalid_login'])
        else:
            self.add_error('email_or_username', self.error_messages['invalid_login'])


class SignUpForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = get_sign_up_fields()

    first_name = forms.CharField(label=_('First Name'), max_length=50, required=False, help_text=_('Optional.'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    last_name = forms.CharField(label=_('Last Name'), max_length=50, required=False, help_text=_('Optional.'))
    email = forms.EmailField(label=_('Email'), max_length=255, help_text=_('Required. Type a valid email address.'),
                             widget=forms.EmailInput(attrs={'placeholder': '@'}))

    error_messages = {
        'unique_email': _('You can not use this email.'),
    }

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()

        email = cleaned_data.get('email', '').lower()

        num_users = UserModel.objects.filter(email=email).count()
        if num_users > 0:
            self.add_error('email', self.error_messages['unique_email'])


class ReSendActivationCodeForm(forms.Form):
    email_or_username = forms.CharField(
        label=_('Email or Username'),
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    error_messages = {
        'non_expired': _('Activation code has already been sent. You can request a new code in 24 hours.'),
        'incorrect_data': _('You entered incorrect data.'),
        'already_activated': _('This profile has already been activated.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ReSendActivationCodeForm, self).clean()

        email_or_username = cleaned_data.get('email_or_username', '')

        try:
            email = email_or_username.lower()
            username = email_or_username

            user = UserModel.objects.filter(
                Q(username=username) | Q(email=email)
            ).first()

            if user.is_active:
                self.add_error('email_or_username', self.error_messages['already_activated'])
            else:
                now_with_shift = timezone.now() - timedelta(hours=24)

                activation = user.activation_set.get()

                if activation.created_at > now_with_shift:
                    self.add_error('email_or_username', self.error_messages['non_expired'])
                else:
                    self.user_cache = user
        except (UserModel.DoesNotExist, Activation.DoesNotExist):
            self.add_error('email_or_username', self.error_messages['incorrect_data'])

    def get_user(self):
        return self.user_cache


class ReSendActivationCodeViaEmailForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    error_messages = {
        'non_expired': _('Activation code has already been sent. You can request a new code in 24 hours.'),
        'incorrect_data': _('You entered incorrect data.'),
        'already_activated': _('This profile has already been activated.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ReSendActivationCodeViaEmailForm, self).clean()

        email = cleaned_data.get('email', '')

        try:
            email = email.lower()

            user = UserModel.objects.filter(email=email).get()

            if user.is_active:
                self.add_error('email', self.error_messages['already_activated'])
            else:
                now_with_shift = timezone.now() - timedelta(hours=24)

                activation = user.activation_set.get()

                if activation.created_at > now_with_shift:
                    self.add_error('email', self.error_messages['non_expired'])
                else:
                    self.user_cache = user
        except (UserModel.DoesNotExist, Activation.DoesNotExist):
            self.add_error('email', self.error_messages['incorrect_data'])

    def get_user(self):
        return self.user_cache


class PasswordResetViaEmailOrUsernameForm(forms.Form):
    email_or_username = forms.CharField(
        label=_('Email or Username'),
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    error_messages = {
        'incorrect_data': _('You entered incorrect data.'),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PasswordResetViaEmailOrUsernameForm, self).clean()

        email_or_username = cleaned_data.get('email_or_username', '')

        try:
            username = email_or_username
            email = email_or_username.lower()

            user = UserModel.objects.filter(
                Q(username=username) | Q(email=email)
            ).first()

            if not user.is_active:
                self.add_error('email_or_username', self.error_messages['inactive'])
            else:
                self.user_cache = user
        except UserModel.DoesNotExist:
            self.add_error('email_or_username', self.error_messages['incorrect_data'])

    def get_user(self):
        return self.user_cache


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(label=_('First Name'), max_length=50, required=False, help_text=_('Optional.'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    last_name = forms.CharField(label=_('Last Name'), max_length=50, required=False, help_text=_('Optional.'))


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=255, widget=forms.EmailInput(attrs={'placeholder': '@'}))

    error_messages = {
        'email_already_exists': _('You can not use this mail.'),
        'same_email': _('Please enter another email.'),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ChangeEmailForm, self).clean()

        email = cleaned_data.get('email', '').lower()

        if email == self.user.email:
            self.add_error('email', self.error_messages['same_email'])
        else:
            user = UserModel.objects.filter(
                Q(email=email) & ~Q(id=self.user.id)
            ).exists()

            if user:
                self.add_error('email', self.error_messages['email_already_exists'])
