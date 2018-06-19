from django.urls import path

from .views import (
    SignInView, ReSendActivationCodeView, SignUpView, ActivateView,
    ChangeEmailView, ChangeEmailActivateView, ChangeProfileView, RecoverUsernameView,
    LogoutView, PasswordResetView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('activate/resend/', ReSendActivationCodeView.as_view(), name='resend_activation_code'),

    path('register/', SignUpView.as_view(), name='register'),
    path('activate/<code>/', ActivateView.as_view(), name='activate'),

    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('recover/username/', RecoverUsernameView.as_view(), name='recover_username'),

    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('change/profile/', ChangeProfileView.as_view(), name='change_profile'),

    path('change/email/', ChangeEmailView.as_view(), name='change_email'),
    path('change/email/<code>/', ChangeEmailActivateView.as_view(), name='change_email_activation'),
]
