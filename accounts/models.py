from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.dispatch import receiver
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class UserManager(BaseUserManager):
	def create_user(self, email, nickname, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not nickname:
			raise ValueError('Users must have an nickname')
		if not password:
			raise ValueError('Users must have an password')

		user = self.model(
			email=self.normalize_email(email),
			nickname=nickname,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, nickname, password):
		user = self.create_user(email=email, nickname=nickname, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user


class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
	)
	nickname = models.CharField(
		verbose_name='nickname',
		max_length=30,
		blank=False,
		unique=False,
		default='',
	)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['nickname', ]

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.email

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	description = models.CharField(max_length=100, blank=True)
	follow_set = models.ManyToManyField('self', blank=True, through='Relation', symmetrical=False, )
	avatar = ProcessedImageField(
		upload_to='avatars/%Y/%m/%d/', 
		processors=[ResizeToFill(150, 150)],
		format = 'JPEG',	
		options = {'quality': 60},
		default ='avatars/default.jpg'
	)
	slug = models.SlugField(allow_unicode=True, default='')


	def __str__(self):
		return self.user.nickname

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			slug = slugify(instance.nickname, allow_unicode=True)
			Profile.objects.create(user=instance, slug=slug)

	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		slug = slugify(instance.nickname, allow_unicode=True)
		if not instance.profile.slug:
			instance.profile.slug = slug
		else:
			instance.profile.slug = slug
		instance.profile.save()

	@property
	def get_follower(self):
		return [i.from_user for i in self.follower_user.all().select_related('from_user__user__profile')]

	@property
	def get_following(self):
		return [i.to_user for i in self.follow_user.all().select_related('to_user__user__profile')]

	@property
	def get_pk_follower(self):
		return self.follower_user.all().values_list('from_user', flat=True)

	@property
	def follower_count(self):
		return len(self.get_follower)

	@property
	def following_count(self):
		return len(self.get_following)

	@property
	def get_joining(self):
		return [i.to_club for i in self.join_user.all().select_related('to_club')]

	@property
	def get_joining_title(self):
		return self.join_user.all().values_list('to_club__title', flat=True)

	@property
	def joining_count(self):
		return len(self.get_joining)


class Relation(models.Model):
	from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follow_user')
	to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower_user')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} -> {}".format(self.from_user, self.to_user)

	class Meta:
		unique_together = (('from_user', 'to_user'),)


class Club(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=30, unique=True)
	slug = models.SlugField(allow_unicode=True, unique=True)
	thumbnail = ProcessedImageField(
		upload_to='clubs/%Y/%m/%d/', 
		processors=[ResizeToFill(200, 200)],
		format = 'JPEG',	
		options = {'quality': 80},
	)
	description = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self):
		slug = slugify(self.title, allow_unicode=True)
		if not self.slug:
			self.slug = slug
		else:
			self.slug = slug
		return super(Club, self).save()

	class Meta:
		ordering = ['-created_at']

	@property
	def get_joiner(self):
		return [i.from_user for i in self.joiner_user.all().select_related('from_user__user__profile')]

	@property
	def get_pk_joiner(self):
		return self.joiner_user.all().values_list('from_user', flat=True)

	@property
	def joiner_count(self):
		return len(self.get_joiner)



class Club_Relation(models.Model):
	from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='join_user')
	to_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='joiner_user')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} -> {}".format(self.from_user, self.to_club)

	class Meta:
		unique_together = (('from_user', 'to_club'),)