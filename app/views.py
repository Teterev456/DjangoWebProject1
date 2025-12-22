"""
Definition of views.
"""

from datetime import datetime
from mailbox import Message
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpRequest
from .forms import AnketaForm, ManagerCommentForm, ManagerOrderForm, OrderCommentForm, OrderForm 
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib import messages
from .models import Blog, CardsProduct, Order
from .models import Comment # использование модели комментариев
from .forms import CommentForm # использование формы ввода комментария
from .forms import BlogForm


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Главная страница',
            'year':datetime.now().year,
        }
    )

def catalog(request):
    """Renders the catalog page."""
    assert isinstance(request, HttpRequest)
    category = request.GET.get('category', 'all')
    cards = CardsProduct.objects.all()
    if category != 'all':
        cards = cards.filter(category=category)
    categories = [choice[0] for choice in CardsProduct.CATEGORY_CHOICES]
    return render(
        request,
        'app/catalog.html',
        {
            'title':'Каталог',
            'cards': cards,
            'selected_category': category,
            'categories': categories,
            'year':datetime.now().year,
        }
    )


def detailcard(request, parametr):
    """Renders the detailcard page."""
    assert isinstance(request, HttpRequest)
    card_1 = CardsProduct.objects.get(id=parametr)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            order.service = card_1
            order.cost = card_1.cost
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            messages.success(
                request, 
                f'Заказ успешно оформлен! Номер вашего заказа: #{order.id}. '
                f'Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('myorders')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = OrderForm()
    
    return render(
        request,
        'app/detailcard.html',
        {
            'card_1': card_1,
            'OrderForm': form,
            'title': card_1.title,
            'year': datetime.now().year,
        }
    )

def myorders(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    order_forms = []  # Список для хранения (заказ, форма)
    
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        form = OrderCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.order = order
            comment.author = request.user
            comment.save()
            messages.success(request, f"Комментарий к заказу #{order.order_number} добавлен!")
            return redirect('myorders')
        else:
            # Если ошибка валидации - сохраняем форму с ошибками для этого заказа
            for o in orders:
                if o.id == int(order_id):
                    order_forms.append((o, form))
                else:
                    order_forms.append((o, OrderCommentForm()))
    else:
        # Для GET-запроса все пустые формы
        for order in orders:
            order_forms.append((order, OrderCommentForm()))
    
    return render(request, 'app/myorders.html', {'order_forms': order_forms})

def orderdetail(request, order_number):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, order_number=order_number)

    if request.method == "POST":
        form = OrderCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.order = order
            comment.author = request.user
            comment.save()
            return redirect('order_detail', order_number=order_number)
    else:
        form = OrderCommentForm()
    
    context = {
        'order': order,
        'OrderCommentForm': form,
        'comments': order.comments.all()
    }
    return render(request, 'app/orderdetail.html', context)

def add_order_comment(request, order_number):
    assert isinstance(request, HttpRequest)
    order = Order.objects.get(Order, order_number=order_number)

    if order.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому заказу')
        return redirect('user_orders')
    
    if request.method == 'POST':
        form = OrderCommentForm(request.POST, request.FILES)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.order = order
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('order_detail', order_number=order_number)
        else:
            messages.error(request, 'Ошибка при добавлении комментария')
    
    return redirect('order_detail', order_number=order_number)

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Полезные ссылки',
            'year':datetime.now().year,
        }
    )

def contacts(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contacts.html',
        {
            'title':'Контактная информация',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'О нас',
            'year':datetime.now().year,
        }
    )

def videopost(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/videopost.html',
        {
            'title':'Видео',
            'year':datetime.now().year,
        }
    )

def pool(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    data = None
    gender = {'1': 'Мужчина', '2': 'Женщина'}
    comfort = {'1': 'Удобно', '2': 'В основном удобно', '3': 'В основном неудобно', '4': 'Неудобно'}
    if request.method == 'POST':
        form = AnketaForm(request.POST)
        if form.is_valid():
            data = dict()
            data['name'] = form.cleaned_data['name']
            data['city'] = form.cleaned_data['city']
            data['job'] = form.cleaned_data['job']
            data['gender'] = gender[ form.cleaned_data['gender'] ]
            data['comfort'] = comfort[ form.cleaned_data['comfort'] ]
            if(form.cleaned_data['notice'] == True):
                data['notice'] = 'Да'
            else:
                data['notice'] = 'Нет'
            data['email'] = form.cleaned_data['email']
            data['message'] = form.cleaned_data['message']
            form = None
    else:
        form = AnketaForm()
    return render(
        request,
        'app/pool.html',
        {
            'form':form,
            'data':data,
        }
    )

def registration(request):
    """Renders the registration page."""
    assert isinstance(request, HttpRequest)
    if request.method == "POST": # после отправки формы
        regform = UserCreationForm (request.POST)
        if regform.is_valid(): #валидация полей формы
            reg_f = regform.save(commit=False) # не сохраняем автоматически данные формы
            reg_f.is_staff = False # запрещен вход в административный раздел
            reg_f.is_active = True # активный пользователь
            reg_f.is_superuser = False # не является суперпользователем
            reg_f.date_joined = datetime.now() # дата регистрации
            reg_f.last_login = datetime.now() # дата последней авторизации
            reg_f.save() # сохраняем изменения после добавления данных
            return redirect('home') # переадресация на главную страницу после регистрации
    else:
        regform = UserCreationForm() # создание объекта формы для ввода данных нового пользователя
    return render(
        request,
        'app/registration.html',
        {
            'regform': regform, # передача формы в шаблон веб-страницы
            'year':datetime.now().year,
        }
    )

def blog(request):
    """Renders the blog page."""
    assert isinstance(request, HttpRequest)
    posts = Blog.objects.all() # запрос на выбор всех статей блога из модели
    return render(
        request,
        'app/blog.html',
        {
            'title':'Блог',
            'posts': posts, # передача списка статей в шаблон веб-страницы
            'year':datetime.now().year,
        }
    )

def blogpost(request, parametr):
    """Renders the blogpost page."""
    assert isinstance(request, HttpRequest)
    post_1 = Blog.objects.get(id=parametr) # запрос на выбор конкретной статьи по параметру
    comments = Comment.objects.filter(post=parametr)

    if request.method == "POST": # после отправки данных формы на сервер методом POST
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user # добавляем (так как этого поля нет в форме) в модель Комментария (Comment) в поле автор авторизованного пользователя
            comment_f.date = datetime.now() # добавляем в модель Комментария (Comment) текущую дату
            comment_f.post = Blog.objects.get(id=parametr) # добавляем в модель Комментария (Comment) статью, для которой данный комментарий
            comment_f.save() # сохраняем изменения после добавления полей
            return redirect('blogpost', parametr=post_1.id) # переадресация на ту же страницу статьи после отправки комментария
    else:
        form = CommentForm() # создание формы для ввода комментария

    return render(
        request,
        'app/blogpost.html',
        {
            'post_1': post_1, # передача конкретной статьи в шаблон веб-страницы
            'comments': comments, # передача всех комментариев к данной статье в шаблон веб-страницы
            'form': form, # передача формы добавления комментария в шаблон веб-страницы
            'year':datetime.now().year,
        }
    )

def newpost(request):
    assert isinstance(request, HttpRequest)
    if request.method == "POST":
        blogform = BlogForm(request.POST, request.FILES)
        if blogform.is_valid():
            blog_f = blogform.save(commit=False)
            blog_f.posted = datetime.now()
            blog_f.author = request.user
            blog_f.save()
            return redirect('blog')
    else:
        blogform = BlogForm()

    return render(
        request,
        'app/newpost.html',
        {
            'blogform': blogform,
            'title': 'Добавить статью блога',
            'year': datetime.now().year,
        }
    )

def is_manager(user):
    """Проверка прав менеджера"""
    return user.is_authenticated and (
        user.is_superuser or 
        user.groups.filter(name='Managers').exists()
    )


def manager_dashboard(request):
    status_filter = request.GET.get('status', 'all')

    if status_filter == 'all':
        orders = Order.objects.all().order_by('-date')
    else:
        orders = Order.objects.filter(status=status_filter).order_by('-date')
    context = {
        'orders': orders,
        'current_status': status_filter
    }
    return render(request, 'app/manager/dashboard.html', context)

def manager_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_form = ManagerOrderForm(instance=order)
    comment_form = ManagerCommentForm()

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        
        if form_type == 'order':
            order_form = ManagerOrderForm(request.POST, instance=order)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, f"Статус заказа №{order.order_number} обновлен!")
                return redirect('manager_order_detail', order_id=order_id)
        
        elif form_type == 'comment':
            comment_form = ManagerCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.order = order
                comment.author = request.user
                comment.save()
                messages.success(request, "Комментарий добавлен!")
                return redirect('manager_order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'order_form': order_form,
        'comment_form': comment_form,
        'comments': order.comments.all().order_by('-created_at')
    }
    return render(request, 'app/manager/order_detail.html', context)

