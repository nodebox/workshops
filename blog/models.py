from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Blog(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text='Blog name, eg. "NodeBox Workshop 2013 Antwerp"')
    slug = models.SlugField(unique=True, help_text='Blog URL, eg. "2013-antwerp"')
    description = models.CharField(max_length=200, help_text='Short about text, eg. "Data Visualization Workshop in Antwerp, 12-16 March 2013."')
    position = models.IntegerField(default=1, unique=True, help_text='Ordering of the blog. Blogs are sorted from low to high, ie. 1 comes first, then 2, 3, etc.')

    def __unicode__(self):
        return self.name

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

    class Meta:
        verbose_name_plural = 'entries'
        db_table = 'blog_entries'
        unique_together = [['blog', 'slug']]


ASSET_TYPE_CHOICES = [['image', 'Image'],
                      ['pdf', 'PDF'],
                      ['zip', 'Zip Archive']]


class Asset(models.Model):
    entry = models.ForeignKey(Entry)
    file_name = models.CharField(max_length=200, help_text='File name of the asset.')
    type = models.CharField(max_length=16, choices=ASSET_TYPE_CHOICES)
    description = models.CharField(max_length=200, help_text='Description of the asset.', blank=True)
    position = models.IntegerField(default=1, unique=True, help_text='Ordering of the asset. Assets are sorted from low to high, ie. 1 comes first, then 2, 3, etc.')

    class Meta:
        unique_together = [['entry', 'position']]
        db_table = 'blog_assets'
