from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.urls import reverse, reverse_lazy
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileEditForm
from django.contrib.auth import get_user_model
from django.http import Http404

from django.utils import timezone

from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView,
    DetailView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin


User = get_user_model()


class PostMixin:
    """Базовый миксин для представлений работы с постами"""

    model = Post
    template_name = 'blog/create.html'


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    """Представление для создания нового поста"""

    form_class = PostForm

    def form_valid(self, form):
        """Устанавливает автора поста перед сохранением"""

        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на профиль автора после создания"""

        return reverse("blog:profile", args=[self.request.user])


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    """Представление для редактирования существующего поста"""

    form_class = PostForm
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста"""

        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправляет на страницу поста после редактирования"""

        return reverse('blog:post_detail', kwargs={'id': self.kwargs['id']})


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    """Представление для удаления поста"""

    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста"""

        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавляет форму в контекст для подтверждения удаления"""

        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """Перенаправляет на профиль автора после удаления"""

        return reverse("blog:profile", kwargs={"username": self.request.user})


class IndexView(ListView):
    """Главная страница со списком опубликованных постов"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает только опубликованные посты с проверенными категориями"""

        return (
            self.model.objects.select_related('location', 'author', 'category')
            .filter(is_published=True,
                    category__is_published=True,
                    pub_date__lte=datetime.now())
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))


class PostDetailView(DetailView):
    """Детальное представление поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        """Возвращает пост с проверкой прав доступа"""

        try:
            post = get_object_or_404(
                self.model.objects.select_related('location', 'author', 'category'),
                pk=self.kwargs['id']
            )
            
            # Проверяем условия видимости поста
            is_visible = (
                post.is_published
                and post.category.is_published
                and post.pub_date <= timezone.now()
            )

            # Если пост не виден и пользователь не автор - 404
            if not is_visible and self.request.user != post.author:
                raise Http404("Пост не найден")

            return post
        except self.model.DoesNotExist:
            raise Http404("Пост не найден")

    def get_context_data(self, **kwargs):
        """Добавляет форму комментария и список комментариев в контекст"""

        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        context['user'] = self.request.user
        return context


class CategoryPostsView(ListView):
    """Список постов в конкретной категории"""

    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        """Возвращает посты выбранной категории"""

        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        current_datetime = datetime.now()
        return self.category.posts.filter(
            pub_date__lte=current_datetime,
            is_published=True
        ).annotate(comment_count=Count("comment")).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        """Добавляет категорию в контекст"""

        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    """Профиль пользователя с его постами"""

    model = Post
    paginate_by = 10
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'

    def get_queryset(self):
        """Возвращает посты конкретного пользователя"""

        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))

    def get_context_data(self, **kwargs):
        """Добавляет профиль пользователя в контекст"""

        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""

    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя"""

        return self.request.user

    def get_success_url(self):
        """Перенаправляет на профиль после редактирования"""

        return reverse('blog:profile', args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария"""

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    post_obj = None

    def get_post_data(self, kwargs):
        """Получает пост, к которому добавляется комментарий"""

        return get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            pub_date__lte=datetime.now(),
            is_published=True,
            category__is_published=True,
        )

    def dispatch(self, request, *args, **kwargs):
        """Сохраняет пост перед обработкой запроса"""

        self.post_obj = self.get_post_data(kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Устанавливает автора и пост перед сохранением комментария"""

        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу поста после создания комментария"""

        return reverse("blog:post_detail", kwargs={'id': self.kwargs['post_id']})


class CommentMixin(LoginRequiredMixin, View):
    """Базовый миксин для работы с комментариями"""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором комментария"""

        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправляет на страницу поста"""

        return reverse("blog:post_detail", kwargs={'id': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    """Редактирование существующего комментария"""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария"""

    success_url = None 

    def get_success_url(self):
        """Перенаправляет на страницу поста после удаления"""

        return reverse("blog:post_detail", kwargs={'id': self.kwargs['post_id']})
