from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.urls import reverse, reverse_lazy

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.core.paginator import Paginator
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView,
    DetailView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


User = get_user_model()


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['id']})


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model.objects.select_related('location', 'author', 'category')
            .filter(pub_date__lte=datetime.now(),
                    is_published=True,
                    category__is_published=True), pk=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


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


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])


def get_post_data(kwargs):
    return get_object_or_404(
        Post,
        pk=kwargs['post_id'],
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True,
    )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_post_data(kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'id': self.kwargs['post_id']})


class CommentMixin(LoginRequiredMixin, View):
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'id': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...
