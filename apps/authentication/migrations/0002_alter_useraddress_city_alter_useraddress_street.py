# Generated by Django 5.0.7 on 2024-07-29 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='street',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Улица'),
        ),
    ]
