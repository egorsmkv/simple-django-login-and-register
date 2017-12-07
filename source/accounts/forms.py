from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import Activation


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    first_name = forms.CharField(max_length=50, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=50, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=255, help_text='Required. Type a valid email address.')

    def send_activation_email(self, request, user):
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
