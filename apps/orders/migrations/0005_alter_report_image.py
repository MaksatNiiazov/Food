# Generated by Django 5.0.7 on 2024-07-22 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_report_telegrambottoken_report_channels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='reports/'),
        ),
    ]
