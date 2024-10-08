# Generated by Django 5.0.7 on 2024-07-23 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_distancepricing_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='closing_hours',
            field=models.TimeField(blank=True, null=True, verbose_name='Время закрытия'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='opening_hours',
            field=models.TimeField(blank=True, null=True, verbose_name='Время открытия'),
        ),
    ]
