# Generated by Django 2.0 on 2018-01-16 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0013_auto_20180114_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Urgent'), (2, 'Pressé'), (3, 'Normal'), (4, 'Y a le temps'), (5, 'Y a vraiment le temps'), (6, 'A considérer'), (7, 'Résolu')], default=3),
        ),
    ]
