from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .models import Post, Category
from .forms import PostForm
from django.urls import reverse


def post(request, id=None):
    if id is not None:
        instance = get_object_or_404(Post, id=id)
    else:
        instance = None
    form = PostForm(request.POST or None, files=request.FILES or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/creat.html', context)

def delete_post(request, id):
    instance = get_object_or_404(Post, id=id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/creat.html', context)


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
