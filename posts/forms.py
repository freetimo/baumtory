from django import forms
from .models import Post, Comment, CATEGORY_CHOICES


class PostForm(forms.ModelForm):
	thumbnail = forms.ImageField(required=True)
	description = forms.CharField(required=False)
	choice = forms.ChoiceField(choices=CATEGORY_CHOICES)

	class Meta:
		model = Post
		fields = ('title', 'thumbnail', 'choice', 'content', 'description', 'published')


class PostEditForm(forms.ModelForm):
	description = forms.CharField(required=False)
	choice = forms.ChoiceField(choices=CATEGORY_CHOICES)

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