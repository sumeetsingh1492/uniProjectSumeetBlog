from django.contrib import admin
from .models import Blog, BlogSeries, BlogCategory, Comment
from tinymce.widgets import TinyMCE
from django.db import models

# Register your models here.
class BlogAdmin(admin.ModelAdmin):
	fieldsets = [
		("Title/date", {"fields": ["blog_title", "blog_published"]}),
		("URL", {"fields":["blog_slug"]}),
		("Series", {"fields":["blog_series"]}),
		("Content", {"fields":["blog_content"]})
	]

	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()}
	}

#Tried using a decorator instead of admin.site.register
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(BlogSeries)
admin.site.register(BlogCategory)

admin.site.register(Blog, BlogAdmin)