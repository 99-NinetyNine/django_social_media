# Generated by Django 3.0.6 on 2020-05-30 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testy', '0005_auto_20200530_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermedia',
            name='is_photo',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
