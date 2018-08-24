from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .forms import UserCreationForm, UserChangeForm
from .models import Profile, Relation, Club, Club_Relation

User = get_user_model()

class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('id', 'email', 'nickname', 'is_active', 'is_admin')
	list_display_links = ['nickname', 'email']
	list_filter = ('is_admin', 'is_active',)
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Personal info', {'fields': ('nickname', )}),
		('Permissions', {'fields': ('is_admin', )}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'nickname', 'password1', 'password2')}
		),
	)
	search_fields = ('email', 'nickname')
	ordering = ('id', )
	filter_horizontal = ()

class FollowInline(admin.TabularInline):
	model = Relation
	fk_name = 'from_user'

class ProfileAdmin(admin.ModelAdmin):
	list_display = ['id', 'user', 'follower_count', 'following_count']
	list_display_links = ['id', 'user', ]
	search_fields = ['id', ]
	readonly_fields = ('follower_count', 'following_count')

	inlines = [FollowInline, ]

class ClubInline(admin.TabularInline):
	model = Club_Relation

class ClubAdmin(admin.ModelAdmin):
	list_display = ['id', 'title', ]
	list_display_links = ['id', 'title', ]
	search_fields = ['id', 'title']

	inlines = [ClubInline, ]

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.unregister(Group)