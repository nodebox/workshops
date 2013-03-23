from django.contrib import admin

from blog.models import Blog, Entry, Asset


class BlogAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'position']
    prepopulated_fields = {'slug': ['name']}


class EntryAdmin(admin.ModelAdmin):
    list_display = ['blog', 'title', 'user', 'pub_date']
    list_display_links = ['title']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'pub_date'
    list_filter = ['blog']
    search_fields = ['title', 'body']


class AssetAdmin(admin.ModelAdmin):
    list_display = ['blog', 'entry', 'file_name']
    list_display_links = ['file_name']


admin.site.register(Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Asset, AssetAdmin)
