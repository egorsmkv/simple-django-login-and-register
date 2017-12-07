from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Activation


class SignInViaEmailForm(forms.Form):
    redirect_field_name = REDIRECT_FIELD_NAME

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': '@', 'focus': True}),
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
            try:
                email = email.lower()
                self.user_cache = User.objects.filter(email=email).first()
                self.confirm_login_allowed(self.user_cache)

                # Check the password
                if not self.user_cache.check_password(password):
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'email': email},
                    )

            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': email},
                )

        return self.cleaned_data

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

    @staticmethod
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
