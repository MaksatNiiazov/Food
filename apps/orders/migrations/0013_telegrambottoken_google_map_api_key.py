# Generated by Django 5.0.7 on 2024-07-30 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_telegrambottoken_app_download_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegrambottoken',
            name='google_map_api_key',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Ключ для карты'),
        ),
    ]
