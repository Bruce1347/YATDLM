# Generated by Django 2.0 on 2018-01-18 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0016_followup_writer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, max_length=700),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=300),
        ),
    ]
