from datetime import timedelta

from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class SignInViaEmailForm(forms.Form):
    redirect_field_name = REDIRECT_FIELD_NAME

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': '@', 'autofocus': True}),
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput,
    )

    error_messages = {
        'invalid_login': _(
            'Please enter a correct %(email)s and password. Note that both '
            'fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            email = email.lower()
            self.user_cache = User.objects.filter(email=email).first()
            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)

                if not self.user_cache.check_password(password):
                    self.invalid_login(email)
            else:
                self.invalid_login(email)

        return self.cleaned_data

    def invalid_login(self, email):
        raise forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'email': email},
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    first_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'))
    last_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'))
    email = forms.EmailField(max_length=255, help_text=_('Required. Type a valid email address.'))

    error_messages = {
        'unique_email': _('You can not use this email.'),
    }

    def clean(self):
        email = self.cleaned_data.get('email')

        if email is not None:
            email = email.lower()
            num_users = User.objects.filter(email=email).count()

            if num_users > 0:
                raise forms.ValidationError(
                    self.error_messages['unique_email'],
                    code='unique_email',
                )

        return self.cleaned_data


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
        email_or_username = self.cleaned_data.get('email_or_username')

        if email_or_username is not None:
            try:
                user = User.objects.filter(
                    Q(username=email_or_username) | Q(email=email_or_username)
                ).get()

                if user.is_active:
                    raise forms.ValidationError(
                        self.error_messages['already_activated'],
                        code='already_activated',
                    )
                else:
                    now_with_shift = timezone.now() - timedelta(hours=24)
                    activation = user.activation_set.get()

                    if activation.created_at > now_with_shift:
                        raise forms.ValidationError(
                            self.error_messages['non_expired'],
                            code='non_expired',
                        )
                    else:
                        self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['incorrect_data'],
                    code='incorrect_data',
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
