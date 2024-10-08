# Generated by Django 5.0.7 on 2024-07-24 05:38

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_tag_remove_ingredient_name_ky_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='name_ky',
            field=models.CharField(max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_ru',
            field=models.CharField(max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='background_color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет фона'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='text_color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет текста'),
        ),
    ]
