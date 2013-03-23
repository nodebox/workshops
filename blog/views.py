
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect

from blog.models import Blog, Entry, Asset


def redirect_to_latest(request):
    blogs = list(Blog.objects.all())
    if len(blogs) > 0:
        return redirect(blogs[0])
    else:
        return HttpResponse('No blogs yet.')


def blog_about(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    return render_to_response('blog/page.html', {'blog': blog, 'title': 'About', 'body': blog.about})


def entry_list(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    entries = blog.entry_set.all()
    return render_to_response('blog/entry_list.html', {'blog': blog, 'entries': entries})


def entry_detail(request, blog_slug, entry_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    entry = get_object_or_404(Entry, blog__slug=blog_slug, slug=entry_slug)
    return render_to_response('blog/entry_detail.html', {'blog': blog, 'entry': entry})
