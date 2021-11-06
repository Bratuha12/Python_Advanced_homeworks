from django.db import models
from django.conf import settings


class UrlShortener(models.Model):
    objects = models.Manager()  # необходимо для корректной работы Pycharm Community Edition
    url_original = models.CharField(max_length=256)
    url_short = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    redirect_count = models.IntegerField(null=True, default=0)
