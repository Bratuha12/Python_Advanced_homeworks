from random import randint

from django.db import models
from django.conf import settings
from django.urls import reverse
# Стандартный slugify django не поддерживает кириллицу, для её поддержки
# используется пакет pytils, который необходимо доустановить
from pytils.translit import slugify


class Post(models.Model):
    # определение objects необходимо для корректной работы
    # Pycharm Community Edition
    objects = models.Manager()
    title = models.CharField(max_length=256)
    text = models.TextField()
    slug = models.SlugField(max_length=70, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL, blank=True,
                                   null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """
        Здесь устанавливается прямой URL для объекта, так что даже
        при возможном изменении структуры URL в будущем, ссылка на некий объект
        останется прежней.
        """
        return reverse('post_detail', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        """
        Метод отвечает за автоматическую генерацию поля slug модели, с помощью
        переопределения метода save(). Слаг генерируется из атрибута title
        только один раз при создании нового объекта. Атрибут __class__ содержит
        ссылку на класс, к которому принадлежит экземпляр (self). Также
        проводится проверка на уникальность сгенерированного слага и
        при необходимости проводится его уникализация.
        """
        if not self.pk:
            self.slug = slugify(self.title)
            ref_class = self.__class__
            while ref_class.objects.filter(slug=self.slug).exists():
                self.slug = f'{self.slug}-{randint(1, 100)}'
        super(Post, self).save(*args, **kwargs)
