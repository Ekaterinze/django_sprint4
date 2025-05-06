from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .models import Post, Category
from .forms import PostForm
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/creat.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(PostMixin, CreateView):
    pass


class PostUpdateView(PostMixin, UpdateView):
    pass


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/creat.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('blog:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем полный объект поста в контекст
        context['post'] = self.get_object()
        return context


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'  # Указываем, что параметр в URL называется 'id'

    def get_object(self, queryset=None):
        current_datetime = datetime.now()  
        return get_object_or_404(
            Post,
            id=self.kwargs['id'],  # Используем self.kwargs['id'] вместо id
            is_published=True,
            pub_date__lte=current_datetime,
            category__is_published=True
        )


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        # Получаем категорию и сохраняем в атрибуте класса
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        current_datetime = datetime.now()
        # Возвращаем отфильтрованные посты
        return self.category.posts.filter(
            pub_date__lte=current_datetime,
            is_published=True
        ).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем категорию в контекст
        context['category'] = self.category
        return context
