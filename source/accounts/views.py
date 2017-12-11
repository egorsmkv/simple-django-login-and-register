from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView, SuccessURLAllowedHostsMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, resolve_url
from django.utils.http import is_safe_url
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.conf import settings

from .utils import get_login_form, send_activation_email, get_password_reset_form, send_reset_password_email
from .forms import SignUpForm, ReSendActivationCodeForm
from .models import Activation


class SuccessRedirectView(SuccessURLAllowedHostsMixin, FormView):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class SignInView(SuccessRedirectView):
    template_name = 'accounts/login.html'
    form_class = get_login_form()
    success_url = '/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class SignUpView(FormView):
    template_name = 'accounts/register.html'
    form_class = SignUpForm
    success_url = '/'

    def form_valid(self, form):
        if settings.ENABLE_USER_ACTIVATION:
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_activation_email(self.request, user)

            messages.add_message(self.request, messages.SUCCESS,
                                 'You are registered. To activate the account, follow the link sent to the mail.')
        else:
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=raw_password)
            login(self.request, user)

            messages.add_message(self.request, messages.SUCCESS, 'You are successfully registered!')

        return super().form_valid(form)


class ActivateView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'index'

    def get_redirect_url(self, *args, **kwargs):
        assert 'code' in kwargs

        act = get_object_or_404(Activation, code=kwargs['code'])

        # Activate user's profile
        user = act.user
        user.is_active = True
        user.save()

        # Remove activation record, it is unneeded
        act.delete()

        messages.add_message(self.request, messages.SUCCESS, 'You have successfully activated your account!')
        login(self.request, user)

        return super().get_redirect_url()


class ReSendActivationCodeView(SuccessRedirectView):
    template_name = 'accounts/resend_activation_code.html'
    form_class = ReSendActivationCodeForm
    success_url = '/'

    def form_valid(self, form):
        user = form.get_user()

        activation = user.activation_set.get()
        activation.delete()

        send_activation_email(self.request, user)

        messages.add_message(self.request, messages.SUCCESS, 'A new activation code has been sent to your e-mail.')

        return HttpResponseRedirect(self.get_success_url())


class PasswordResetView(BasePasswordResetView):
    form_class = get_password_reset_form()

    def form_valid(self, form):
        send_reset_password_email(self.request, form.get_user())

        return HttpResponseRedirect(self.get_success_url())
