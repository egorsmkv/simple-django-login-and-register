from django.urls import path

from .views import (
    SignInView, ReSendActivationCodeView, SignUpView, ActivateView,
    ChangeEmailView, ChangeEmailActivateView, ProfileEditView,
    LogoutView, PasswordResetView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)

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

    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),

    path('change/email/', ChangeEmailView.as_view(), name='change_email'),
    path('change/email/<code>/', ChangeEmailActivateView.as_view(), name='change_email_activation'),
]
