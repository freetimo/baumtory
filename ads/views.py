from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from .forms import AdForm
from .models import Ad

@login_required
def ad(request, pk, slug):
	ads = Ad.objects.filter(user=request.user)
	today = date.today()
	if request.method == 'POST':
		form = AdForm(request.POST, request.FILES)
		if form.is_valid():
			form = form.save(commit=False)
			form.user = request.user
			form.save()
			return redirect('ad', pk=request.user.profile.pk, slug=request.user.profile.slug)
	else:
		form = AdForm()
	return render(request, 'ad.html', {'form': form, 'ads': ads, 'today': today})