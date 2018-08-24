from django import forms
from .models import Post, Comment
from accounts.models import Club_Relation

class PostForm(forms.ModelForm):
	def __init__(self, profile, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		iquery = [('No choice', 'No choice')] + [(str(i.to_club.title), str(i.to_club.title)) for i in Club_Relation.objects.filter(from_user=profile).select_related('to_club')]
		self.fields['choice'] = forms.ChoiceField(choices=iquery)

	thumbnail = forms.ImageField(required=True)
	description = forms.CharField(required=False)

	class Meta:
		model = Post
		fields = ('title', 'choice', 'thumbnail', 'content', 'description', 'published')


class PostEditForm(forms.ModelForm):
	def __init__(self, profile, *args, **kwargs):
		super(PostEditForm, self).__init__(*args, **kwargs)
		iquery = [('No choice', 'No choice')] + [(str(i.to_club.title), str(i.to_club.title)) for i in Club_Relation.objects.filter(from_user=profile).select_related('to_club')]
		self.fields['choice'] = forms.ChoiceField(choices=iquery)
		
	description = forms.CharField(required=False)

	class Meta:
		model = Post
		fields = ('title', 'choice', 'content', 'description', 'published')


class PostThumbnailForm(forms.ModelForm):
	thumbnail = forms.ImageField(required=True)

	class Meta:
		model = Post
		fields = ('thumbnail',)


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('comment', )

	def queryset(self, request):
		return super(CommentForm, self).queryset(request).select_related('user__profile')