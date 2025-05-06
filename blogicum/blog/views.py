from django.shortcuts import render, get_object_or_404
from datetime import datetime
from .models import Post, Category


def index(request):
    template = 'blog/index.html'
    current_datetime = datetime.now()
    posts = Post.objects.filter(
        pub_date__lte=current_datetime,  # __lte - меньше или равно
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')[:5]

    context = {'post_list': posts}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    current_datetime = datetime.now()
    post = get_object_or_404(
        Post,
        id=id,
        is_published=True,
        pub_date__lte=current_datetime,
        category__is_published=True
    )

    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    current_datetime = datetime.now()

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts.filter(
        pub_date__lte=current_datetime,
        is_published=True
    ).order_by('-pub_date')

    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)
