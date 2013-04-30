import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.text import slugify

from blog.models import Blog, Post, Asset


def redirect_to_latest(request):
    blogs = list(Blog.objects.all())
    if len(blogs) > 0:
        return redirect(blogs[0])
    else:
        return HttpResponse('No blogs yet.')


def blog_about(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    return render_to_response('blog/page.html', {'blog': blog, 'title': 'About', 'body': blog.about})


def post_list(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    posts = blog.post_set.all()
    return render_to_response('blog/post_list.html', {'blog': blog, 'posts': posts})


def post_list_by_author(request, blog_slug, username):
    blog = get_object_or_404(Blog, slug=blog_slug)
    user = get_object_or_404(User, username=username)
    posts = blog.post_set.filter(user=user)
    return render_to_response('blog/post_list_by_author.html', {'blog': blog, 'author': user, 'posts': posts})


def post_detail(request, blog_slug, username, post_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    post = get_object_or_404(Post, blog__slug=blog_slug, user__username=username, slug=post_slug)
    return render_to_response('blog/post_detail.html', {'blog': blog, 'post': post})


@login_required
def post_list_by_user(request):
    posts = request.user.post_set.all()
    return render_to_response('blog/post_list_by_user.html',
                              {'user': request.user, 'posts': posts})


class PostForm(forms.Form):
    title = forms.CharField(max_length=100)
    body = forms.CharField(widget=forms.Textarea)
    image_1 = forms.FileField(required=False)
    image_2 = forms.FileField(required=False)
    image_3 = forms.FileField(required=False)


@login_required
def post_create(request):
    blog = Blog.objects.get(slug='2013-montreal')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post(blog=blog,
                        user=request.user,
                        title=form.cleaned_data['title'],
                        slug=slugify(form.cleaned_data['title']),
                        body=form.cleaned_data['body'])
            post.save()
            _handle_upload(post, request.FILES.get('image_1'), 1)
            _handle_upload(post, request.FILES.get('image_2'), 2)
            _handle_upload(post, request.FILES.get('image_3'), 3)
            return redirect(post)
    else:
        form = PostForm()

    return render_to_response('blog/post_create.html',
                              {'user': request.user, 'blog': blog, 'form': form}, context_instance=RequestContext(request))


def _handle_upload(post, f, position=1):
    if f is not None:
        target_path = _unique_filename(post, f)
        with open(target_path, 'wb+') as target_file:
            for chunk in f.chunks():
                target_file.write(chunk)
        asset = Asset(post=post,
                      file_name=os.path.basename(target_path),
                      type='image',
                      position=position)
        asset.save()
        return asset


def _ensure_media_directory(post):
    dir = os.path.join(settings.MEDIA_ROOT, post.blog.slug)
    if not os.path.exists(dir):
        os.makedirs(dir)


def _unique_filename(post, f):
    full_path = _full_path(post, f.name)
    if not os.path.exists(full_path):
        return full_path
    else:
        filename, ext = os.path.splitext(f.name)
        for i in range(1, 100):
            full_path = _full_path(post, '%s_%s%s' % (filename, i, ext))
            if not os.path.exists(full_path):
                return full_path


def _full_path(post, filename):
    return '%s/%s/%s' % (settings.MEDIA_ROOT, post.blog.slug, filename)
