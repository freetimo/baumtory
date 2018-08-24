from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.http import JsonResponse
from django.db import transaction
from .forms import UserCreationForm, UserChangeForm, ProfileAvatarForm, ProfileDescriptionForm, ClubCreationForm, ClubThumbnailForm, ClubDescriptionForm
from .models import Profile, Relation, Club, Club_Relation
from posts.models import Post

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
      messages.success(request, 'Your profile was successfully updated!')
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
      message = 'Cancel to Follow'
      status = 0

  ctx = {
      'message': message,
      'status': status,
  }
  return JsonResponse(ctx)


@login_required
def followers(request, pk, slug):
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
def following(request, pk, slug):
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

  
@login_required
def joining_club(request, pk, slug):
  join_set = request.user.profile.get_joining
  page = request.GET.get('page', 1)

  paginator = Paginator(join_set, 20)
  try:
    clubs = paginator.page(page)
  except PageNotAnInteger:
    clubs = paginator.page(1)
  except EmptyPage:
    clubs = paginator.page(paginator.num_pages)

  return render(request, 'join_clubs.html', {'clubs': clubs})


@login_required
@require_POST
def join(request):
  from_user = request.user.profile
  pk = request.POST.get('pk')
  to_club = get_object_or_404(Club, pk=pk)
  relation, created = Club_Relation.objects.get_or_create(from_user=from_user, to_club=to_club)

  if created:
      message = 'Start to join'
      status = 1
  else:
      relation.delete()
      message = 'Cancel to join'
      status = 0

  ctx = {
      'message': message,
      'status': status,
      'joiner_count': to_club.joiner_count
  }
  return JsonResponse(ctx)

class ClubsListView(ListView):
  queryset = Club.objects.exclude(title='No choice')
  template_name = 'clubs.html'
  context_object_name = 'clubs'
  paginate_by = 20


@login_required
def new_club(request):
  if request.method == 'POST':
    form = ClubCreationForm(request.POST, request.FILES)
    if form.is_valid():
      title = ''.join(c for c in request.POST.get('title').capitalize() if c.isalnum() or c == ' ')
      qs = Club.objects.filter(title=title)
      if qs.filter(title=title).exists():
        messages.error(request,'Club with this Title already exists.')
        return redirect('new_club')
      else:
        club = form.save(commit=False)
        club.user = request.user
        club.title = title
        club.save()
        Club_Relation.objects.create(from_user=request.user.profile, to_club=club)
        return redirect('club', slug=club.slug)
  else:
    form = ClubCreationForm()
  return render(request, 'new_club.html', {'form': form})


@login_required
@transaction.atomic
def edit_club(request, slug):
  club = get_object_or_404(Club, slug=slug)
  if request.method == 'POST':
    club_description_form = ClubDescriptionForm(request.POST, instance=club)
    club_thumbnail_form = ClubThumbnailForm(request.POST, request.FILES, instance=club)
    if club_thumbnail_form.is_valid() and club_description_form.is_valid():
      club_thumbnail_form.save()
      club_description_form.save()
      messages.success(request, 'Your club was successfully updated!')
      return redirect('edit_club', slug=club.slug)
    else:
      club_description_form = ClubDescriptionForm(instance=club)
      club_thumbnail_form = ClubThumbnailForm()
      ctx = {
        'club': club,
        'club_thumbnail_form': club_thumbnail_form,
        'club_description_form': club_description_form
      }
      messages.success(request, "Something went wrong!")
      return redirect('edit_club', slug=club.slug)
  else:
    club_description_form = ClubDescriptionForm(instance=club)
    club_thumbnail_form = ClubThumbnailForm()
    ctx = {
    'club': club,
    'club_thumbnail_form': club_thumbnail_form,
    'club_description_form': club_description_form
    }
  return render(request, 'edit_club.html', ctx)


def club(request, slug):
  club = get_object_or_404(Club.objects.select_related('user',), slug=slug)
  post = Post.objects.filter(choice=club.title).exclude(published=False).select_related('user__profile',)

  page = request.GET.get('page', 1)
  paginator = Paginator(post, 20)
  try:
    posts = paginator.page(page)
  except PageNotAnInteger:
    posts = paginator.page(1)
  except EmptyPage:
    posts = paginator.page(paginator.num_pages)

  ctx = {
    'club': club,
    'posts': posts,
  }
  return render(request, 'club.html', ctx)


def members(request, slug):
  club = get_object_or_404(Club, slug=slug)
  member_set = club.get_joiner
  page = request.GET.get('page', 1)

  paginator = Paginator(member_set, 20)
  try:
    members = paginator.page(page)
  except PageNotAnInteger:
    members = paginator.page(1)
  except EmptyPage:
    members = paginator.page(paginator.num_pages)

  ctx = {
  'members': members, 
  'club': club
  }
  return render(request, 'members.html', ctx)