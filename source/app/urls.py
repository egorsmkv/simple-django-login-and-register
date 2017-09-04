from django.conf.urls import url
from django.contrib import admin

from django.contrib.auth import views as auth_views

import main.views
import accounts.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', main.views.index_page),

    url(r'^accounts/register/$', accounts.views.register, name='register'),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
