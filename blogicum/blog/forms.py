from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

User = get_user_model()


BEATLES = {'Джон Леннон', 'Пол Маккартни', 'Джордж Харрисон', 'Ринго Старр'}


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        exclude = ['is_published', 'author']
        # Указываем, что надо отобразить все поля.
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def clean(self):
        super().clean()
        title = self.cleaned_data['title']
        if f'{title}' in BEATLES:
            # Отправляем письмо, если кто-то представляется
            # именем одного из участников Beatles.
            send_mail(
                subject='Another Beatles member',
                message=f'{title} пытался опубликовать запись!',
                from_email='Blog_form@acme.not',
                recipient_list=['admin@acme.not'],
                fail_silently=True,
            )
            raise ValidationError(
                'Мы тоже любим Битлз, но введите, пожалуйста, настоящее имя!'
            )
