# Generated by Django 3.0.6 on 2020-06-07 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testy', '0010_auto_20200607_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='reply',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='testy.Comments'),
        ),
    ]
