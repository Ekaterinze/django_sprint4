from django.db import models
from django.contrib.auth import get_user_model
from core.models import PublishedCreatedModel

User = get_user_model()


class Category(PublishedCreatedModel):
    """Модель категории для публикаций"""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Уникальный идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        """Строковое представление категории"""

        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)


class Location(PublishedCreatedModel):
    """Модель местоположения для публикаций"""

    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    def __str__(self):
        """Строковое представление местоположения"""

        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)


class Post(PublishedCreatedModel):
    """Основная модель публикации (поста)"""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    image = models.ImageField(
        'Фото',
        upload_to='post_images',
        blank=True
    )

    def __str__(self):
        """Строковое представление публикации"""

        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        indexes = [
            models.Index(fields=['-pub_date', 'author']),
        ]


class Comment(models.Model):
    """Модель комментария к публикации"""
    text = models.TextField(
        'Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='публикация'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['created_at', 'author'])
        ]

    def __str__(self):
        """Строковое представление комментария"""

        return f"Комментарий пользователя {self.author}"
