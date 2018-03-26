from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views as auth
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

import main.views
import accounts.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', main.views.IndexPageView.as_view(), name='index'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', main.views.ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/login/', accounts.views.SignInView.as_view(), name='login'),
    path('accounts/logout/', auth.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    path('accounts/activate/resend/', accounts.views.ReSendActivationCodeView.as_view(), name='resend_activation_code'),

    path('accounts/register/', accounts.views.SignUpView.as_view(), name='register'),
    path('accounts/activate/<code>/', accounts.views.ActivateView.as_view(), name='activate'),

    path('accounts/password/change/', auth.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html'), name='password_change'),
    path('accounts/password/change/done/', auth.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),

    path('accounts/password/reset/',
         accounts.views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('accounts/password/reset/done/', auth.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/',
         auth.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),

    path('accounts/profile/edit/', accounts.views.ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/change/email/', accounts.views.ChangeEmailView.as_view(), name='change_email'),
    path('accounts/change/email/<code>/', accounts.views.ChangeEmailActivateView.as_view(),
         name='change_email_activation'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns()
