# Generated by Django 2.1 on 2018-11-27 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lang_app', '0004_auto_20181127_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='block',
            name='block_type',
        ),
        migrations.AddField(
            model_name='qanda',
            name='qanda_type',
            field=models.CharField(default='explore', max_length=1024),
        ),
    ]