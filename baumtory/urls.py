from django.urls import re_path, path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from posts import views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('new/post/', views.new_post, name='new'),
    path('upload/image/', views.upload_image, name='upload_image'),
    path('post/<int:pk>/<str:slug>/', views.post_detail, name='detail'),
    path('edit/post/<int:pk>/<str:slug>/', views.edit_post, name='edit_post'),
    path('delete/post/<int:pk>/<str:slug>/', views.PostDeleteView.as_view(), name='delete'),
    path('like/post/', views.post_like, name='post_like'),
    path('dislike/post/', views.post_dislike, name='post_dislike'),
    path('explore/', accounts_views.ClubsListView.as_view(), name='clubs'),
    path('club/no-choice/', TemplateView.as_view(
            template_name="404.html",
        ), 
        name='no-choice'),
    path('club/<str:slug>/', accounts_views.club, name='club'),
    path('edit/club/<str:slug>/', accounts_views.edit_club, name='edit_club'),
    path('members/club/<str:slug>/', accounts_views.members, name='members'),
    path('make/club/', accounts_views.new_club, name='new_club'),
    path('join/', accounts_views.join, name='join'),
    path('feed/follow/', views.FollowPostListView.as_view(), name='follow_post'),
    path('follow/', accounts_views.follow, name='follow'),
    path('feed/bookmark/', views.BookmarkListView.as_view(), name='bookmark_post'),
    path('bookmark/', views.bookmark, name='bookmark'),
    path('reply/load/', views.reply_load, name='reply_load'),
    path('comment/like/', views.comment_like, name='comment_like'),
    path('comment/dislike/', views.comment_dislike, name='comment_dislike'),
    path('comment/new/', views.comment_new, name='comment_new'),
    path('comment/delete/', views.comment_delete, name='comment_delete'),
    path('diary/<int:pk>/<str:slug>/', views.diary, name='diary'),
    path('followers/diary/<int:pk>/<str:slug>/', accounts_views.followers, name='followers'),
    path('following/diary/<int:pk>/<str:slug>/', accounts_views.following, name='following'),
    path('clubs/diary/<int:pk>/<str:slug>/', accounts_views.joining_club, name='joining_club'),
    path('result/', views.SearchListView.as_view(), name='search'),
    path('signup/', accounts_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout' ),
    path('settings/profile/edit/', accounts_views.edit_user, name='edit_user'),
    path('reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html', 
            email_template_name='password_reset_email.html', 
            subject_template_name='password_reset_subject.txt'
        ), 
        name='password_reset'),
    path('reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), 
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),
    path('reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'),
    path('settings/password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='password_change.html'
        ),
        name='password_change'),
    path('settings/password/change/done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'
        ), 
        name='password_change_done'), 
    path('google9a6563a74745c84f.html', TemplateView.as_view(
            template_name="google9a6563a74745c84f.html"
        ), name="google_search_console"),
    path('robots.txt/', TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ), 
        name="project_robots_file"),
    path('help_bear/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'posts.views.handler404'
handler500 = 'posts.views.handler500'