from django.db import models
from django.urls import reverse


class News(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование')
    content = models.TextField(blank=True, verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True,
                              verbose_name='Фото')
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано')
    # Название связанной модели 'Category' указываем в кавычках,
    # потому что данная модель описана ниже.
    category = models.ForeignKey('Category', on_delete=models.PROTECT,
                                 verbose_name='Категория')
    views = models.IntegerField(default=0)

    def get_absolute_url(self):  # получение абсолютной ссылки на пост
        return reverse('view_news', kwargs={'pk': self.pk})

    class Meta:  # Настройка админки "под себя"
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at', 'title']


class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True,
                             verbose_name='Наименование категории')

    def get_absolute_url(self):  # получение абсолютной ссылки на категорию
        return reverse('category', kwargs={'category_id': self.pk})

    # Строковое представление объекта для вывода читаемой строки в админке
    def __str__(self):
        return self.title

    class Meta:  # Настройка админки "под себя"
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']
