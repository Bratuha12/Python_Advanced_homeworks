# Generated by Django 3.2.7 on 2021-10-29 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UrlShortener',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_original', models.CharField(max_length=256)),
                ('url_short', models.CharField(max_length=100)),
            ],
        ),
    ]