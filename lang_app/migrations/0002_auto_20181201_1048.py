# Generated by Django 2.1 on 2018-12-01 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lang_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='block_size',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_size',
            field=models.IntegerField(default=6),
        ),
    ]
