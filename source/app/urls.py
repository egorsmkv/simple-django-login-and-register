from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path

import main.views
import accounts.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', main.views.index_page, name='index'),

    path('accounts/login/', accounts.views.SignInView.as_view(), name='login'),
    path('accounts/logout/', auth.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    path('accounts/register/', accounts.views.SignUpView.as_view(), name='register'),
    path('accounts/activate/<code>/', accounts.views.ActivateView.as_view(), name='activate'),

    path('accounts/password/change/', auth.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html'), name='password_change'),
    path('accounts/password/change/done/', auth.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),

    path('accounts/password/reset/', auth.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('accounts/password/reset/done/', auth.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),

    path('accounts/password/<uidb64>/<token>/',
         auth.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('accounts/password/reset/done/',
         auth.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
