from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('creat/', views.post, name='creat_post'),
    path('<int:id>/edit/', views.post, name='edit_post'),
    path('<int:id>/delete/', views.delete_post, name='delete_post'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
]
