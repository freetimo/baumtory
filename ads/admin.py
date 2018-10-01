from django.contrib import admin
from .models import Ad

class AdAdmin(admin.ModelAdmin):
	list_per_page = 50
	list_display_links = ['id', 'title', ]
	list_display = ('id', 'published', 'exposure', 'start_date', 'end_date', 'name', 'title', 'web', 'choice', 'user',)
	search_fields = ('title',)
	
admin.site.register(Ad, AdAdmin)