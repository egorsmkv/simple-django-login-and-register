from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.contrib import messages

from .forms import SignUpForm


def register(request):
    ctx = dict()
    ctx.update(csrf(request))

    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=raw_password)
            login(request, user)

            messages.add_message(request, messages.SUCCESS, 'You are successfully registered!')

            return redirect('/')

    ctx['form'] = form

    return render(request, 'accounts/register.html', ctx)
