# Generated by Django 2.1 on 2018-11-27 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lang_app', '0005_auto_20181127_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstate',
            name='split',
            field=models.FloatField(blank=True, default=0.5, null=True),
        ),
    ]
