# Generated by Django 3.1.6 on 2021-04-28 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='max_subs',
            field=models.IntegerField(default=99999),
        ),
    ]
