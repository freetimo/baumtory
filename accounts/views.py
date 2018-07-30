from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from .forms import UserCreationForm, UserChangeForm, ProfileAvatarForm, ProfileDescriptionForm
from .models import Profile, Relation

User = get_user_model()
 
def signup(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      auth_login(request, user)
      return redirect('home')
  else:
  	form = UserCreationForm()
  return render(request, 'signup.html', {'form': form})


@login_required
@transaction.atomic
def edit_user(request):
  if request.method == 'POST':
    user_form = UserChangeForm(request.POST, instance=request.user)
    profile_avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=request.user.profile)
    profile_description_form = ProfileDescriptionForm(request.POST, instance=request.user.profile)
    if user_form.is_valid() and profile_avatar_form.is_valid() and profile_description_form.is_valid():
      user_form.save()
      profile_avatar_form.save()
      profile_description_form.save()
      messages.success(request, 'Your profile has been successfully updated!')
      return redirect('edit_user')
    else:
      ctx = {
        'user_form': user_form, 
        'profile_avatar_form': profile_avatar_form,
        'profile_description_form': profile_description_form
      }
  else:
    user_form = UserChangeForm(instance=request.user)
    profile_avatar_form = ProfileAvatarForm(instance=request.user)
    profile_description_form = ProfileDescriptionForm(instance=request.user.profile)
    ctx = {
      'user_form': user_form, 
      'profile_avatar_form': profile_avatar_form,
      'profile_description_form': profile_description_form
    }
  return render(request, 'edit_user.html', ctx)

@login_required
@require_POST
def follow(request):
  from_user = request.user.profile
  pk = request.POST.get('pk')
  to_user = get_object_or_404(Profile, pk=pk)
  relation, created = Relation.objects.get_or_create(from_user=from_user, to_user=to_user)

  if created:
      message = 'Start to follow'
      status = 1
  else:
      relation.delete()
      message = 'Stop following'
      status = 0

  ctx = {
      'message': message,
      'status': status,
  }
  return JsonResponse(ctx)


@login_required
def followers(request, pk):
  follow_set = request.user.profile.get_follower
  page = request.GET.get('page', 1)

  paginator = Paginator(follow_set, 20)
  try:
    follows = paginator.page(page)
  except PageNotAnInteger:
    follows = paginator.page(1)
  except EmptyPage:
    follows = paginator.page(paginator.num_pages)
  return render(request, 'followers.html', {'follows': follows})

  
@login_required
def following(request, pk):
  follow_set = request.user.profile.get_following
  page = request.GET.get('page', 1)

  paginator = Paginator(follow_set, 20)
  try:
    follows = paginator.page(page)
  except PageNotAnInteger:
    follows = paginator.page(1)
  except EmptyPage:
    follows = paginator.page(paginator.num_pages)

  return render(request, 'following.html', {'follows': follows})