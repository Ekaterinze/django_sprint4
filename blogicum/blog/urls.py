from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('creat/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('<int:id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]
