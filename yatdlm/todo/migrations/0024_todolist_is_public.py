# Generated by Django 2.0 on 2018-02-17 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0023_auto_20180213_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='todolist',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]