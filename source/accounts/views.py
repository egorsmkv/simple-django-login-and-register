from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.conf import settings

from .forms import SignUpForm
from .models import Activation


class SignUpView(FormView):
    template_name = 'accounts/register.html'
    form_class = SignUpForm
    success_url = '/'

    def form_valid(self, form):
        if settings.ENABLE_USER_ACTIVATION:
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            form.send_activation_email(self.request, user)

            messages.add_message(self.request, messages.SUCCESS,
                                 'Are you registered. To activate, follow the link sent to the mail.')
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
