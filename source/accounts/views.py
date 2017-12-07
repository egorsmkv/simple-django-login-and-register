from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import FormView

from .forms import SignUpForm


class SignUpView(FormView):
    template_name = 'accounts/register.html'
    form_class = SignUpForm
    success_url = '/'

    def form_valid(self, form):
        form.save()

        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')

        user = authenticate(username=username, password=raw_password)
        login(self.request, user)

        messages.add_message(self.request, messages.SUCCESS, 'You are successfully registered!')

        return super().form_valid(form)
