"""
Definition of models.
"""

from django.utils import timezone as tz
from django.db import models
from django.contrib import admin
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Blog(models.Model):
    title = models.CharField(max_length = 100, unique_for_date = "posted", verbose_name = "Заголовок")
    author = models.ForeignKey(User, null=True, blank=True, on_delete = models.SET_NULL, verbose_name = "Автор")
    description = models.TextField(verbose_name = "Краткое содержание")
    content = models.TextField(verbose_name = "Полное содержание")
    posted = models.DateTimeField(default = datetime.now(), db_index = True, verbose_name = "Опубликована")
    image = models.FileField(default = 'tmp.jpg', verbose_name = "Путь к картинке")

    # Методы класса:
    def get_absolute_url(self): # метод возвращает строку с URL-адресом записи
        return reverse("blogpost", args=[str(self.id)])

    def __str__(self): # метод возвращает название, используемое для представления отдельных записей в административном разделе
        return self.title

    # Метаданные – вложенный класс, который задает дополнительные параметры модели:

    class Meta:
        db_table = "Posts" # имя таблицы для модели
        ordering = ["-posted"] # порядок сортировки данных в модели ("-" означает по убыванию)
        verbose_name = "Статья блога" # имя, под которым модель будет отображаться в административном разделе (для одной статьи блога)
        verbose_name_plural = "статьи блога" # тоже для всех статей блога
admin.site.register(Blog)

class Comment(models.Model):
    text = models.TextField(verbose_name = "Текст комментария")
    date = models.DateTimeField(default = datetime.now(), db_index = True, verbose_name = "Дата комментария")
    author = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = "Автор комментария")
    post = models.ForeignKey(Blog, on_delete = models.CASCADE, verbose_name = "Статья комментария")

    def __str__(self): 
        return 'Комментарий %d %s k %s' % (self.id, self.author, self.post)

    class Meta:
        db_table = "Comment"
        ordering = ["-date"]
        verbose_name = "Комментарий к статье блога"
        verbose_name_plural = "Комментарии к статьям блога"

admin.site.register(Comment)

class CardsProduct(models.Model):
    image = models.ImageField(default = '', verbose_name = "Изображение товара")
    title = models.CharField(max_length = 100, unique = True, verbose_name = "Заголовок")
    description = models.TextField(verbose_name = "Краткое содержание")
    content = models.TextField(verbose_name = "Полное содержание")
    cost = models.DecimalField(max_digits = 10, default = 100.00, verbose_name="Цена", decimal_places = 2)
    is_available = models.BooleanField(default = True, verbose_name = "В наличии")
    CATEGORY_CHOICES = [('photo_sessions', 'Фотосессии'),('printed_products', 'Печатная продукция'),('service_packages', 'Пакеты услуг'),]
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES,default='photo_sessions',verbose_name='Категория')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = "Catalog"
        verbose_name = "Карточка товара"
        verbose_name_plural = "Карточки товаров"

admin.site.register(CardsProduct)

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="URL-имя")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

admin.site.register(Category)

class Order(models.Model):
    STATUS_CHOICES = [('new', 'Новый'),
        ('processing', 'В обработке'),
        ('confirmed', 'Подтвержден'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),]

    service = models.ForeignKey(CardsProduct, on_delete=models.CASCADE, verbose_name="Услуга", related_name='orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")

    customer_name = models.CharField(max_length=200, verbose_name="Имя")
    customer_email = models.EmailField(verbose_name="Email")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    customer_message = models.TextField(verbose_name="Сообщение", blank=True)

    date = models.DateTimeField(default = datetime.now(), db_index = True, verbose_name = "Дата заказа")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер заказа")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена")
    prepayment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Предоплата")
    manager_comment = models.TextField(verbose_name="Комментарий менеджера", blank=True)

    def __str__(self):
        return f"Заказ {self.order_number} - {self.service.title}"
    
    def get_status_color_class(self):
        """Возвращает CSS-класс в зависимости от статуса."""
        color_map = {
            'new': 'status-new',
            'processing': 'status-processing',
            'confirmed': 'status-confirmed',
            'in_progress': 'status-in-progress',
            'completed': 'status-completed',
            'cancelled': 'status-cancelled',
        }
        return color_map.get(self.status, 'status-default')

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = tz.now().strftime("%Y%m%d")
            last_order = Order.objects.filter(order_number__startswith=date_str).order_by('order_number').last()
            if last_order:
                last_num = int(last_order.order_number[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f"{date_str}-{new_num:04d}"
        if not self.price:
            self.price = self.service.cost
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('order_detail', kwargs={'order_number': self.order_number})

    class Meta:
        db_table = "Orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date']

admin.site.register(Order)

class OrderComment(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий к заказу #{self.order.id}"
    
    class Meta:
        ordering = ['-created_at']

admin.site.register(OrderComment)

