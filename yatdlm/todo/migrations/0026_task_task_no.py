# Generated by Django 2.1.4 on 2018-12-19 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0025_auto_20180219_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='task_no',
            field=models.IntegerField(default=0),
        ),
    ]