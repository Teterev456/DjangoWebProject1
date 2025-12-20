"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import CardsProduct, Comment, Order, OrderComment, User
from .models import Blog

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': ''}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':''}))
class AnketaForm(forms.Form):
    name = forms.CharField(label="Ваше имя", min_length=2, max_length=100)
    city = forms.CharField(label="Ваш город", min_length=2, max_length=100)
    job = forms.CharField(label="Ваш род занятий", min_length=2, max_length=100)
    gender = forms.ChoiceField(label="Ваш пол", choices=[('1', 'Мужской'), ('2', 'Женский')], widget=forms.RadioSelect, initial=1)
    comfort = forms.ChoiceField(label="Как вы оцените удобство использования сайта", choices=(('1', 'Удобно'), ('2', 'В основном удобно'), ('3', 'В основном неудобно'), ('4', 'Неудобно')), initial=1)
    notice = forms.BooleanField(label="Получать новости сайта на email?", required=False)
    email = forms.EmailField(label='Ваш e-mail:', min_length=7)
    message = forms.CharField(label='Предложения для улучшения удобства использования сайта', max_length=100, widget=forms.Textarea(attrs={'rows':12,'cols':20}))

class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment # используемая модель
        fields = ('text',) # требуется заполнить только поле text
        labels = {'text': "Комментарий"} # метка к полю формы text

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'description', 'content', 'image',)
        labels = {'title': "Заголовок", 'description': 'Краткое содержание', 'content': "Полное содержание", 'image': "Картинка"}

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'customer_message']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67',
                'required': True
            }),
            'customer_message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Дополнительные пожелания',
                'rows': 4
            }),
        }
        labels = {
            'customer_name': 'Ваше имя',
            'customer_email': 'Email (Формат: user123@yandex.ru)',
            'customer_phone': 'Телефон (Формат: +7 (999) 123-45-67)',
            'customer_message': 'Комментарий к заказу',
        }

class OrderCommentForm(forms.ModelForm):
    class Meta:
        model = OrderComment
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите ваш комментарий или вопрос по заказу...',
                'required': True
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'text': 'Ваш комментарий',
            'file': 'Прикрепить файл (опционально)'
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            max_size = 5 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError(
                    f'Размер файла не должен превышать 5MB. Ваш файл: {file.size/1024/1024:.1f}MB'
                )
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    f'Разрешенные форматы: {", ".join(allowed_extensions)}'
                )
        return file
