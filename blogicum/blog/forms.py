from django import forms
from .models import Post, Comment
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm


User = get_user_model()

# Список имен участников группы Beatles для проверки
BEATLES = {'Джон Леннон', 'Пол Маккартни', 'Джордж Харрисон', 'Ринго Старр'}


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария"""

    class Meta:
        model = Comment
        fields = ('text',)

class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста"""

    class Meta:
        model = Post
        exclude = ['is_published', 'author']  # Исключаем эти поля из формы
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }

    def clean(self):
        """Кастомная валидация формы с проверкой имени автора"""

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
