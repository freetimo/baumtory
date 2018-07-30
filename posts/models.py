from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

User = get_user_model()

CATEGORY_CHOICES = (
	("no choice", "No choice"),
	("fun", "Fun"),
	("lifestyle", "Lifestyle"),
	("review", "Review"),
	("information", "Information"),
	("thought", "Thought")
)

class Post(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	slug = models.SlugField(allow_unicode=True, default='')
	thumbnail = ProcessedImageField(
		upload_to='thumbnails/%Y/%m/%d/', 
		processors=[ResizeToFill(300, 200)],
		format = 'JPEG',	
		options = {'quality': 80},
	)
	choice = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
	content = JSONField(blank=True, null=True)
	published = models.BooleanField(default=False)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	published_at = models.DateTimeField(auto_now=True)
	likes = models.ManyToManyField(User, blank=True, related_name='likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')

	def __str__(self):
		return self.title	

	def publish(self):
		self.published = True

	class Meta:
		ordering = ['-created_at']

	def save(self):
		slug = slugify(self.title, allow_unicode=True)
		if not self.slug:
			self.slug = slug
		else:
			self.slug = slug
		return super(Post, self).save()

	@property
	def total_likes(self):
		return self.likes.count() 

	@property
	def total_dislikes(self):
		return self.dislikes.count() 


class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	reply = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='replies')
	comment = models.CharField(max_length=200)
	created_at = models.DateTimeField(auto_now_add=True)
	likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')

	def __str__(self):
		return self.comment

	class Meta:
		ordering = ['-created_at']

	@property
	def total_likes(self):
		return self.likes.count() 

	@property
	def total_dislikes(self):
		return self.dislikes.count() 


class Bookmark(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.post.title

	class Meta:
		ordering = ['-created_at']