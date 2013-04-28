from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
    url(r'^$', views.redirect_to_latest, name='redirect_to_latest'),
    url(r'^posts/$', views.post_list_by_user, name='post_list_by_user'),
    url(r'^posts/new/$', views.post_create, name='post_create'),
    url(r'^(?P<blog_slug>[\w-]+)/$', views.post_list, name='post_list'),
    url(r'^(?P<blog_slug>[\w-]+)/about/$', views.blog_about, name='blog_about'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<username>[\w-]+)/$', views.post_list_by_author, name='post_list_by_author'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<username>[\w-]+)/(?P<post_slug>[\w-]+)/$', views.post_detail, name='post_detail')
)
