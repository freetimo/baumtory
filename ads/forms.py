from django import forms
from .models import Ad, Choice


class AdForm(forms.ModelForm):
	choice = forms.ChoiceField(choices=Choice, widget=forms.RadioSelect())
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

	class Meta:
		model = Ad
		fields = ('start_date', 'end_date', 'choice', 'name', 'email', 'image', 'title', 'web')