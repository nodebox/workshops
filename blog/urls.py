from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
    url(r'^$', views.redirect_to_latest, name='redirect_to_latest'),
    url(r'^(?P<blog_slug>[\w-]+)/$', views.entry_list, name='entry_list'),
    url(r'^(?P<blog_slug>[\w-]+)/about/$', views.blog_about, name='blog_about'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<entry_slug>[\w-]+)/$', views.entry_detail, name='entry_detail')
)
