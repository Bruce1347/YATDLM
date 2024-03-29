# Generated by Django 2.0 on 2018-01-20 09:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("todo", "0020_auto_20180120_0954"),
    ]

    operations = [
        migrations.AlterField(
            model_name="followup",
            name="new_priority",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Commentaire"), (2, "Changement d'État")],
                default=1,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="followup",
            name="old_priority",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Commentaire"), (2, "Changement d'État")],
                default=1,
                null=True,
            ),
        ),
    ]
