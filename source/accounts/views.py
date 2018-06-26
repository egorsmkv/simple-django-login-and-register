from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings

from .utils import (
    send_activation_email, send_reset_password_email, send_forgotten_username, send_activation_change_email,
    is_username_disabled, is_use_remember_me, is_restore_password_via_email_or_username,
)
from .forms import (
    SignInViaEmailForm, SignInViaEmailOrUsernameForm, SignInViaUsernameForm,
    SignUpForm, ChangeProfileForm, ChangeEmailForm, RemindUsernameForm,
    RestorePasswordForm, RestorePasswordViaEmailOrUsernameForm,
    ResendActivationCodeForm, ResendActivationCodeViaEmailForm,
)
from .models import Activation


class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LogInView(GuestOnlyView, FormView):
    template_name = 'accounts/log_in.html'

    @staticmethod
    def get_form_class(**kwargs):
        if hasattr(settings, 'LOGIN_VIA_EMAIL') and settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm

        if hasattr(settings, 'LOGIN_VIA_EMAIL_OR_USERNAME') and settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm

        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # If the test cookie worked, go ahead and delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        # The default Django's "remember me" lifetime is 2 weeks and can be changed by modifying
        # the SESSION_COOKIE_AGE settings' option.
        if is_use_remember_me():
            if not form.cleaned_data.get('remember_me'):
                self.request.session.set_expiry(0)

        login(self.request, form.get_user())

        return redirect(settings.LOGIN_REDIRECT_URL)


class SignUpView(GuestOnlyView, FormView):
    template_name = 'accounts/sign_up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save(commit=False)

        if is_username_disabled():
            # Set temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data.get('username')

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

        # Create a user record
        user.save()

        # Change the username to the "user_ID" form
        if is_username_disabled():
            user.username = f'user_{user.id}'
            user.save()

        if settings.ENABLE_USER_ACTIVATION:
            send_activation_email(self.request, user)

            messages.add_message(self.request, messages.SUCCESS,
                                 _('You are signed up. To activate the account, follow the link sent to the mail.'))
        else:
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(username=user.username, password=raw_password)
            login(self.request, user)

            messages.add_message(self.request, messages.SUCCESS, _('You are successfully signed up!'))

        return redirect('index')


class ActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)

        # Activate user's profile
        user = act.user
        user.is_active = True
        user.save()

        # Remove activation record, it is unneeded
        act.delete()

        messages.add_message(request, messages.SUCCESS, _('You have successfully activated your account!'))
        login(request, user)

        return redirect(settings.LOGIN_REDIRECT_URL)


class ResendActivationCodeView(GuestOnlyView, FormView):
    template_name = 'accounts/resend_activation_code.html'

    @staticmethod
    def get_form_class(**kwargs):
        if is_username_disabled():
            return ResendActivationCodeViaEmailForm

        return ResendActivationCodeForm

    def form_valid(self, form):
        user = form.get_user()

        activation = user.activation_set.get()
        activation.delete()

        send_activation_email(self.request, user)

        messages.add_message(self.request, messages.SUCCESS,
                             _('A new activation code has been sent to your email address.'))

        return redirect('accounts:resend_activation_code')


class RestorePasswordView(GuestOnlyView, FormView):
    template_name = 'accounts/restore_password.html'

    @staticmethod
    def get_form_class(**kwargs):
        if is_restore_password_via_email_or_username():
            return RestorePasswordViaEmailOrUsernameForm

        return RestorePasswordForm

    def form_valid(self, form):
        send_reset_password_email(self.request, form.get_user())

        return redirect('accounts:restore_password_done')


class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_profile.html'
    form_class = ChangeProfileForm

    def get_initial(self):
        initial = super().get_initial()

        user = self.request.user

        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name

        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.save()

        messages.add_message(self.request, messages.SUCCESS, _('Profile data has been successfully updated.'))

        return redirect('accounts:change_profile')


class ChangeEmailView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_email.html'
    form_class = ChangeEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        user = self.request.user

        initial['email'] = user.email

        return initial

    def form_valid(self, form):
        user = self.request.user
        email = form.cleaned_data.get('email', '').lower()

        if hasattr(settings, 'EMAIL_ACTIVATION_AFTER_CHANGING') and settings.EMAIL_ACTIVATION_AFTER_CHANGING:
            send_activation_change_email(self.request, user, email)

            messages.add_message(self.request, messages.SUCCESS,
                                 _('To complete the change of email address, click on the link sent to it.'))
        else:
            user.email = email
            user.save()

            messages.add_message(self.request, messages.SUCCESS, _('Email successfully changed.'))

        return redirect('accounts:change_email')


class ChangeEmailActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)

        # Change user's email
        user = act.user
        user.email = act.email
        user.save()

        # Remove activation record, it is unneeded
        act.delete()

        messages.add_message(request, messages.SUCCESS, _('You have successfully changed your email!'))

        return redirect('accounts:change_email')


class RemindUsernameView(GuestOnlyView, FormView):
    template_name = 'accounts/remind_username.html'
    form_class = RemindUsernameForm

    def form_valid(self, form):
        email = form.cleaned_data.get('email', '').lower()

        send_forgotten_username(email)

        messages.add_message(self.request, messages.SUCCESS,
                             _('Your username has been successfully sent to your email.'))

        return redirect('accounts:remind_username')


class ChangePasswordView(BasePasswordChangeView):
    template_name = 'accounts/change_password.html'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Your password was changed.'))

        return redirect('accounts:change_password')


class RestorePasswordConfirmView(BasePasswordResetConfirmView):
    template_name = 'accounts/restore_password_confirm.html'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             _('Your password has been set. You may go ahead and log in now.'))

        return redirect('accounts:log_in')


class RestorePasswordDoneView(BasePasswordResetDoneView):
    template_name = 'accounts/restore_password_done.html'


class LogOutView(LoginRequiredMixin, BaseLogoutView):
    template_name = 'accounts/log_out.html'
