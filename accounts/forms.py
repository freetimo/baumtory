from django import forms
from django.contrib.auth import get_user_model
from .models import UserManager, Profile, Club

User = get_user_model()

class UserCreationForm(forms.ModelForm):
	email = forms.EmailField(
		label='Email',
		required=True, 
		widget=forms.EmailInput(
			attrs={
				'class': 'validate',
				'required': 'True',
			}
		)
	)
	nickname = forms.CharField(
		label='Nickname',
		required=True,
		widget=forms.TextInput(
			attrs={
				'class': 'validate',
				'required': 'True'
			}
		)
	)
	password1 = forms.CharField(
		label='Password',
		widget=forms.PasswordInput(
			attrs={
				'class': 'validate',
				'required': 'True',
			}
		)
	)
	password2 = forms.CharField(
		label='Password confirmation',
		widget=forms.PasswordInput(
			attrs={
				'class': 'validate',
				'required': 'True',
			}
		)
	)

	class Meta:
		model = User
		fields = ('email', 'nickname')

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.email = UserManager.normalize_email(self.cleaned_data['email'])
		user.nickname = self.cleaned_data['nickname']
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('nickname',)

class ProfileAvatarForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('avatar', )

class ProfileDescriptionForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('description', )


class ClubCreationForm(forms.ModelForm):
	thumbnail = forms.ImageField(required=True)
	class Meta:
		model = Club
		fields = ('title', 'thumbnail', 'description')

class ClubThumbnailForm(forms.ModelForm):
	class Meta:
		model = Club
		fields = ('thumbnail', )

class ClubDescriptionForm(forms.ModelForm):
	class Meta:
		model = Club
		fields = ('description', )