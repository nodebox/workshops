from django.conf.urls import patterns, url

from accounts import views

urlpatterns = patterns('',
    url(r'^login/$', views.accounts_login, name='accounts_login'),
)
