# Generated by Django 2.0 on 2018-01-05 22:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("todo", "0009_task_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="resolution_date",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
