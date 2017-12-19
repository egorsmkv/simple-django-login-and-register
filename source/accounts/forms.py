from datetime import timedelta

from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Activation

UserModel = get_user_model()


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


class SignInViaEmailForm(SignIn):
    field_order = ['email', 'password']

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': '@', 'autofocus': True}),
    )

    error_messages = {
        'invalid_login': _(
            'Please enter a correct %(email)s and password. Note that both '
            'fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            email = email.lower()
            self.user_cache = UserModel.objects.filter(email=email).first()
            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)

                if not self.user_cache.check_password(password):
                    self.invalid_login(email)
            else:
                self.invalid_login(email)

        return self.cleaned_data


class SignInViaEmailOrForm(SignIn):
    field_order = ['email_or_username', 'password']

    email_or_username = forms.CharField(
        label=_('Email or Username'),
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    error_messages = {
        'invalid_login': _(
            'Please enter a correct email or username and password. Note that both '
            'fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email_or_username = self.cleaned_data.get('email_or_username')
        password = self.cleaned_data.get('password')

        if email_or_username is not None and password:
            email = email_or_username.lower()
            username = email_or_username

            self.user_cache = UserModel.objects.filter(
                Q(username=username) | Q(email=email)
            ).first()

            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)

                if not self.user_cache.check_password(password):
                    self.invalid_login(email)
            else:
                self.invalid_login(email)

        return self.cleaned_data


class SignUpForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    first_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    last_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'))
    email = forms.EmailField(max_length=255, help_text=_('Required. Type a valid email address.'),
                             widget=forms.EmailInput(attrs={'placeholder': '@'}))

    error_messages = {
        'unique_email': _('You can not use this email.'),
    }

    def clean(self):
        email = self.cleaned_data.get('email')

        if email is not None:
            email = email.lower()
            num_users = UserModel.objects.filter(email=email).count()

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
                username = email_or_username
                email = email_or_username.lower()

                user = UserModel.objects.filter(
                    Q(username=username) | Q(email=email)
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
            except (UserModel.DoesNotExist, Activation.DoesNotExist):
                raise forms.ValidationError(
                    self.error_messages['incorrect_data'],
                    code='incorrect_data',
                )

        return self.cleaned_data

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
        email_or_username = self.cleaned_data.get('email_or_username')

        if email_or_username:
            try:
                username = email_or_username
                email = email_or_username.lower()

                user = UserModel.objects.filter(
                    Q(username=username) | Q(email=email)
                ).get()

                if not user.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
                else:
                    self.user_cache = user
            except UserModel.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['incorrect_data'],
                    code='incorrect_data',
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    last_name = forms.CharField(max_length=50, required=False, help_text=_('Optional.'))


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(max_length=255, widget=forms.EmailInput(attrs={'placeholder': '@'}))

    error_messages = {
        'email_already_exists': _('You can not use this mail.'),
        'same_email': _('Please enter another email.'),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')

        email = email.lower()

        if email == self.user.email:
            raise forms.ValidationError(
                self.error_messages['same_email'],
                code='same_email',
            )
        else:
            user = UserModel.objects.filter(
                Q(email=email) & ~Q(id=self.user.id)
            ).exists()

            if user:
                raise forms.ValidationError(
                    self.error_messages['email_already_exists'],
                    code='email_already_exists',
                )

        return self.cleaned_data
