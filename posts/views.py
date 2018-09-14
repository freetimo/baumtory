from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
from django.db.models import Q
from posts.models import Post, Comment, Bookmark
from posts.forms import PostForm, CommentForm, PostEditForm, PostThumbnailForm
from accounts.models import Club
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
try:
    from django.utils import simplejson as json
except ImportError:
    import json
import uuid 
import os

User = get_user_model()

def home(request):
	if request.user.is_authenticated:
		choice = request.user.profile.get_joining_title
		post_list = Post.objects.filter(choice__in=choice).exclude(published=False).select_related('user__profile')[:100]
		page = request.GET.get('page', 1)
		paginator = Paginator(post_list, 20)
		try:
			club_posts = paginator.page(page)
		except PageNotAnInteger:
			club_posts = paginator.page(1)
		except EmptyPage:
			club_posts = paginator.page(paginator.num_pages)
		ctx = {
		'club_posts': club_posts,
		}
		return render(request, 'index.html', ctx)
	else:
		post_list = Post.objects.exclude(published=False).select_related('user__profile')[:100]
		page = request.GET.get('page', 1)
		paginator = Paginator(post_list, 20)
		try:
			posts = paginator.page(page)
		except PageNotAnInteger:
			posts = paginator.page(1)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)
		ctx = {
		'posts': posts, 
		}
	return render(request, 'index.html', ctx)

@method_decorator(login_required, name='dispatch')
class FollowPostListView(ListView):
	queryset = Post.objects.exclude(published=False)
	context_object_name ='posts'
	template_name = 'feed_follow.html'
	paginate_by = 24

	def get_queryset(self):
		queryset = super().get_queryset()
		follow_set = self.request.user.profile.get_following
		return queryset.filter(user__profile__in=follow_set).select_related('user__profile')

@method_decorator(login_required, name='dispatch')
class BookmarkListView(ListView):
	queryset = Bookmark.objects.select_related('post__user__profile')
	context_object_name = 'posts'
	template_name = 'feed_bookmark.html'
	paginate_by = 24

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		return queryset.filter(user=user)

class SearchListView(ListView):
	queryset = Post.objects.exclude(published=False).select_related('user__profile')
	context_object_name ='posts'
	template_name = 'search_posts.html'
	paginate_by = 20

	def get_queryset(self):
		queryset = super().get_queryset()
		query = self.request.GET.get("search", None)

		if query is not None:
			queryset = queryset.filter(
				Q(title__icontains=query)|
				Q(description__icontains=query)
				).distinct()
		else:
			raise Http404
		return queryset

def diary(request, pk, slug):
	user = get_object_or_404(User.objects.select_related('profile',), pk=pk)
	post_list = Post.objects.filter(user=user).select_related('user__profile',)
	page = request.GET.get('page', 1)

	paginator = Paginator(post_list, 20)
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	return render(request, 'diary.html', {'posts': posts, 'user':user})

def post_detail(request, pk, slug):
	post = get_object_or_404(Post.objects.select_related('user__profile', ).prefetch_related('likes', 'dislikes'), pk=pk, slug=slug)
	user = post.user
	club = Club.objects.values('slug').get(title=post.choice)
	lt_posts = Post.objects.exclude(published=False).select_related('user__profile', ).filter(Q(user=user) & Q(id__lt=pk))
	gt_posts = Post.objects.exclude(published=False).select_related('user__profile', ).filter(Q(user=user) & Q(id__gt=pk))
	comment_lists = Comment.objects.filter(post=post).select_related('user__profile', 'reply', ).prefetch_related('likes', 'dislikes')
	comment_list = comment_lists.filter(reply=None)
	replies = list(set(comment_lists.values_list('reply', flat=True)))
	commentform = CommentForm()
	page = request.GET.get('page', 1)
	paginator = Paginator(comment_list, 20)
	try:
		comments = paginator.page(page)
	except PageNotAnInteger:
		comments = paginator.page(1)
	except EmptyPage:
		comments = paginator.page(paginator.num_pages)
	ctx = {
		'commentform': commentform, 
		'lt_posts': lt_posts, 
		'gt_posts': gt_posts, 
		'post': post, 
		'club': club,
		'comments': comments,
		'replies': replies
	}
	return render(request, 'post_detail.html', ctx)

@login_required
def new_post(request):
	profile = request.user.profile
	if request.method == 'POST':
		form = PostForm(profile, request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.content = request.POST.get('content')
			if request.POST.get('action') == "save":
				post.save()
				return redirect('edit_post', pk=post.pk, slug=post.slug)
			elif request.POST.get('action') == "submit":
				post.published = True
				post.save()
				return redirect('detail', pk=post.pk, slug=post.slug)  
	else:
		form = PostForm(profile)
	return render(request, 'new_post.html', {'form': form, })

class ResizeImg(ImageSpec):
	processors = [ResizeToFill(810, 540)]
	format = 'JPEG'
	options = {'quality': 80}

@login_required
@require_POST
def upload_image(request):
	now = timezone.now()
	form_data = request.FILES['image']
	image_generator = ResizeImg(source=form_data)
	result = image_generator.generate()
	root = 'image/{year}/{month}/{day}'.format(year=now.year, month=now.month, day=now.day)
	image_folder = os.path.join(settings.MEDIA_ROOT, root)
	if not os.path.exists(image_folder):
		os.makedirs(image_folder)
	file_name = uuid.uuid4().hex[:10]
	target = os.path.join(image_folder, file_name+'.jpg')
	with open(target, 'wb+') as f:
		f.write(result.getvalue())
	url = os.path.join(root, file_name+'.jpg')
	return HttpResponse(json.dumps(url))

@login_required
def edit_post(request, pk, slug):
	profile = request.user.profile
	post = get_object_or_404(Post, pk=pk, slug=slug)
	post_title = post.title
	if request.method == 'POST':
		post_thumbnail_form = PostThumbnailForm(request.POST, request.FILES, instance=post)
		post_edit_form = PostEditForm(profile, request.POST, instance=post)
		if post_edit_form.is_valid() and post_thumbnail_form.is_valid():
			post_thumbnail_form.save()
			post_content = post_edit_form.save(commit=False)
			post_content.content = request.POST.get('content')
			if post_title == request.POST.get('title'):
				if request.POST.get('save'):
					post_content.save()
					message = 'Saved'
					return JsonResponse({'message': message})
				elif request.POST.get('submit'):
					post_content.published = True
					post_content.save()
					return redirect('detail', pk=post.pk, slug=post.slug)
			else:
				if request.POST.get('save'):
					post_content.save()
					response = {
						'status': 1, 
						'message': "Saved",
						'url': resolve_url('edit_post', pk=post.pk, slug=post.slug)
					}
					return JsonResponse(response)
				elif request.POST.get('submit'):
					post_content.published = True
					post_content.save()
					return redirect('detail', pk=post.pk, slug=post.slug)
		else:
			raise Http404
	else:
		post_edit_form = PostEditForm(profile, instance=post)
		post_thumbnail_form = PostThumbnailForm()
		ctx = {
			'post': post,
			'post_edit_form': post_edit_form, 
			'post_thumbnail_form': post_thumbnail_form
		}
	return render(request, 'edit_post.html', ctx)

@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
	model = Post
	template_name = 'delete_post.html'

	def get_success_url(self):
		return reverse_lazy('diary', kwargs={'pk': self.request.user.pk})

def reply_load(request):
	pk = request.POST.get('pk')
	comment = get_object_or_404(Comment, pk=pk)
	replies = Comment.objects.filter(reply=comment).select_related('user__profile', )
	commentform = CommentForm()
	ctx={
		'comment': comment,
		'replies': replies,
		'commentform': commentform
	}
	return render(request, 'reply_load_ajax.html', ctx)

@login_required
@require_POST
def comment_new(request):
	pk = request.POST.get('pk')
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			reply_id = request.POST.get('comment_id')
			comment_qs = None
			if reply_id:
				comment_qs = Comment.objects.get(pk=reply_id)	
			comment.user = request.user
			comment.post = post			
			comment.reply = comment_qs
			comment.save()
			return render(request, 'comment_new_ajax.html', {'comment': comment, })
		else:
			raise Http404
	return redirect('detail', pk=pk)

@login_required
@require_POST
def comment_delete(request):
	pk = request.POST.get('pk')
	comment = get_object_or_404(Comment, pk=pk)
	if request.method == 'POST' and request.user == comment.user:
		comment.delete()
		message = 'Deleted successfully'
		status = 1
	else:
		message = 'Invalid access'
		status = 0

	ctx = {'message': message, 'status': status, }
	return JsonResponse(ctx)

@login_required
@require_POST
def bookmark(request):
	if request.method == 'POST':
		user = request.user
		post_id = request.POST.get('pk')
		post = get_object_or_404(Post, pk=post_id)
		bookmark = Bookmark.objects.filter(user=user, post=post)

	if bookmark.exists():
		bookmark.delete()
		message = 'Deleted successfully'
	else:
		Bookmark.objects.create(user=user, post=post)
		message = 'Added successfully'

	ctx = {'message': message}
	return JsonResponse(ctx)

@login_required
@require_POST
def post_like(request):
	if request.method == 'POST':
		user = request.user
		post_id = request.POST.get('pk', None)
		post = get_object_or_404(Post, pk=post_id)

	if post.likes.filter(id=user.id).exists():
		post.likes.remove(user)
	else:
		post.likes.add(user)

	ctx = {'likes_count': post.total_likes}
	return JsonResponse(ctx)

@login_required
@require_POST
def post_dislike(request):
	if request.method == 'POST':
		user = request.user
		post_id = request.POST.get('pk', None)
		post = get_object_or_404(Post, pk=post_id)
	if post.dislikes.filter(id=user.id).exists():
		post.dislikes.remove(user)
	else:
		post.dislikes.add(user)
	ctx = {'dislikes_count': post.total_dislikes}
	return JsonResponse(ctx)

@login_required
@require_POST
def comment_like(request):
	if request.method == 'POST':
		user = request.user
		comment_id = request.POST.get('pk', None)
		comment = get_object_or_404(Comment, pk=comment_id)
	if comment.likes.filter(id=user.id).exists():
		comment.likes.remove(user)
	else:
		comment.likes.add(user)
	ctx = {'likes_count': comment.total_likes}
	return JsonResponse(ctx)

@login_required
@require_POST
def comment_dislike(request):
	if request.method == 'POST':
		user = request.user
		comment_id = request.POST.get('pk', None)
		comment = get_object_or_404(Comment, pk=comment_id)
	if comment.dislikes.filter(id=user.id).exists():
		comment.dislikes.remove(user)
	else:
		comment.dislikes.add(user)
	ctx = {'dislikes_count': comment.total_dislikes}
	return JsonResponse(ctx)

def handler404(request, exception):
	return render(request, '404.html', status=404)

def handler500(request, exception):
	return render(request, '500.html', status=500)