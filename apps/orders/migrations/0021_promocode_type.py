# Generated by Django 5.0.7 on 2024-09-17 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_promocode_order_promo_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='type',
            field=models.CharField(choices=[('p', 'Процент'), ('f', 'Фиксированная сумма')], default='p', max_length=1, verbose_name='Тип'),
            preserve_default=False,
        ),
    ]
