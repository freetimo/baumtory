from django.db import models
from django.contrib.auth import get_user_model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

User = get_user_model()

Choice = (
	('~30일 50000원', '~30일 50000원'),
	('31일~45일 72000원', '31일~45일 72000원'),
	('46일~60일 90000원', '46일~60일 90000원'),
	('~30일 무료 10개의 포스팅', '~30일 무료 10개의 포스팅'),
)

class Ad(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	start_date = models.DateField()
	end_date = models.DateField()
	choice = models.CharField(max_length=30, choices=Choice)
	email = models.CharField(max_length=70)
	image = ProcessedImageField(
		upload_to='ad/%Y/%m/%d/', 
		processors=[ResizeToFill(300, 200)],
		format = 'JPEG',	
		options = {'quality': 90},
	)
	title = models.CharField(max_length=40)
	web = models.CharField(max_length=200)
	published = models.BooleanField(default=False)
	exposure = models.BooleanField(default=False)

	class Meta:
		ordering = ['-id']