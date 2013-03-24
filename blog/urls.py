from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
    url(r'^$', views.redirect_to_latest, name='redirect_to_latest'),
    url(r'^(?P<blog_slug>[\w-]+)/$', views.post_list, name='post_list'),
    url(r'^(?P<blog_slug>[\w-]+)/about/$', views.blog_about, name='blog_about'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<post_slug>[\w-]+)/$', views.post_detail, name='post_detail')
)
