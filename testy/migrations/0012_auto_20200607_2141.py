# Generated by Django 3.0.6 on 2020-06-07 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testy', '0011_auto_20200607_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='reply',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='testy.Comments'),
        ),
    ]
