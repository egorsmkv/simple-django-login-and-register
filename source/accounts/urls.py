from django.urls import path
from django.contrib.auth.views import (
    LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from .views import (
    SignInView, ReSendActivationCodeView, SignUpView, ActivateView, PasswordResetView,
    ChangeEmailView, ChangeEmailActivateView, ProfileEditView
)

urlpatterns = [
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    path('activate/resend/', ReSendActivationCodeView.as_view(), name='resend_activation_code'),

    path('register/', SignUpView.as_view(), name='register'),
    path('activate/<code>/', ActivateView.as_view(), name='activate'),

    path('password/change/', PasswordChangeView.as_view(template_name='accounts/password_change_form.html'),
         name='password_change'),
    path('password/change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'),

    path('password/reset/', PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password/reset/done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),

    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),

    path('change/email/', ChangeEmailView.as_view(), name='change_email'),
    path('change/email/<code>/', ChangeEmailActivateView.as_view(), name='change_email_activation'),
]
