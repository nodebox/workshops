from django.contrib import admin

from blog.models import Blog, Entry, Asset


class BlogAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


class EntryAdmin(admin.ModelAdmin):
    list_display = ['blog', 'user', 'pub_date', 'title']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'pub_date'
    list_filter = ['blog']
    search_fields = ['title', 'body']

admin.site.register(Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Asset)
