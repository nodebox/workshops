from datetime import datetime
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Blog(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text='Blog name, eg. "NodeBox Workshop 2013 Antwerp"')
    slug = models.SlugField(unique=True, help_text='Blog URL, eg. "2013-antwerp"')
    description = models.CharField(max_length=200, help_text='Short about text, eg. "Data Visualization Workshop in Antwerp, 12-16 March 2013."')
    about = models.TextField(help_text='About page for this blog. Use HTML if you like.')
    position = models.IntegerField(default=1, unique=True, help_text='Ordering of the blog. Blogs are sorted from low to high, ie. 1 comes first, then 2, 3, etc.')

    @property
    def users(self):
        return User.objects.filter(entry__blog=self, is_superuser=False).distinct()

    def get_absolute_url(self):
        return '/%s/' % self.slug

    def __unicode__(self):
        return self.name

    @property
    def assets_directory(self):
        return os.path.join(settings.MEDIA_ROOT, self.slug)

    def ensure_assets_directory(self):
        """Ensure the directory containing this blogs assets exists."""
        try:
            os.makedirs(self.assets_directory)
        except OSError, e:
            if e.errno != 17:  # Don't show an error if the directory already exists.
                raise e

    class Meta:
        db_table = 'blog_blogs'
        ordering = ['position']


class Entry(models.Model):
    blog = models.ForeignKey(Blog)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=200, help_text='Title of the blog post.')
    slug = models.SlugField(help_text='URL of the blog post, eg. "about-my-project"')
    pub_date = models.DateTimeField('date published', default=datetime.now)
    body = models.TextField()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s' % (self.blog.slug, self.slug)

    @property
    def first_image(self):
        try:
            return self.asset_set.all()[0]
        except IndexError:
            return None

    class Meta:
        verbose_name_plural = 'entries'
        db_table = 'blog_entries'
        unique_together = [['blog', 'slug']]
        ordering = ['-pub_date']


ASSET_TYPE_CHOICES = [['image', 'Image'],
                      ['pdf', 'PDF'],
                      ['zip', 'Zip Archive']]


class Asset(models.Model):
    entry = models.ForeignKey(Entry)
    file_name = models.CharField(max_length=200, help_text='File name of the asset.')
    type = models.CharField(max_length=16, choices=ASSET_TYPE_CHOICES)
    description = models.CharField(max_length=200, help_text='Description of the asset.', blank=True)
    position = models.IntegerField(default=1, help_text='Ordering of the asset. Assets are sorted from low to high, ie. 1 comes first, then 2, 3, etc.')

    @property
    def url(self):
        return '%s%s/%s' % (settings.MEDIA_URL, self.entry.blog.slug, self.file_name)

    @property
    def relative_path(self):
        return '%s/%s' % (self.entry.blog.slug, self.file_name)

    @property
    def absolute_path(self):
        return '%s/%s/%s' % (settings.MEDIA_ROOT, self.entry.blog.slug, self.file_name)

    class Meta:
        db_table = 'blog_assets'
        ordering = ['position']
