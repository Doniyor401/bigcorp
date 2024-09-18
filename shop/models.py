from django.db import models
from django.utils.text import slugify
import random
import string
from django.urls import reverse


def rand_slug():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))


class Category(models.Model):
    name = models.CharField(max_length=250, db_index=True, verbose_name='Название категории')
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE,
        null=True, blank=True, verbose_name='Родительская категория'
    )
    slug = models.SlugField(max_length=250, unique=True, null=False, editable=True, verbose_name='URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent

        return ' -> '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + '-pickBetter' + self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category-list', args=[str(self.slug)])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Категория')
    title = models.CharField(max_length=250, verbose_name='Название продукта')
    brand = models.CharField(max_length=250, verbose_name='Бренд')
    description = models.TextField(blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=250, verbose_name='URL')
    price = models.DecimalField(max_digits=7, decimal_places=2, default=99.99, verbose_name='Цена')
    image = models.ImageField(upload_to='products/products/%Y/%m/%d', blank=True, verbose_name='Изображение')
    available = models.BooleanField(default=True, verbose_name='Наличие')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[str(self.slug)])


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):
    objects = ProductManager()

    class Meta:
        proxy = True
