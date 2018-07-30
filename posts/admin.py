from django.contrib import admin
from .models import Post, Comment, Bookmark


class PostAdmin(admin.ModelAdmin):
	list_per_page = 50
	list_display_links = ['id', 'title', ]
	list_display = ('id', 'published', 'title', 'choice', 'user', 'created_at' ,)
	search_fields = ('title', 'description')
	ordering = ('id', )
	ordering = ('-created_at', )
	list_filter = ('created_at',)

class CommentAdmin(admin.ModelAdmin):
	search_fields = ('comment',)
	list_per_page = 50
	list_filter = ('created_at',)
	list_display_links = ['id', 'comment', ]
	list_display = ('id', 'comment', 'reply', 'post', 'created_at')


class BookmarkAdmin(admin.ModelAdmin):
	list_per_page = 50
	list_filter = ('created_at',)
	list_display = ('user', 'post', 'created_at')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bookmark, BookmarkAdmin)