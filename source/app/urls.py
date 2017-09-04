from django.conf.urls import url
from django.contrib import admin

from django.contrib.auth import views as auth

import main.views
import accounts.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', main.views.index_page),

    url(r'^accounts/login/$', auth.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'^accounts/logout/$', auth.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    url(r'^accounts/register/$', accounts.views.register, name='register'),

    url(r'^accounts/password/reset/$', auth.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
        name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),

    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$',
        auth.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
]
