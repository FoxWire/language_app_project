# Generated by Django 2.0.7 on 2018-07-30 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chunk', models.CharField(max_length=1024)),
                ('chunk_translation', models.CharField(max_length=1024)),
                ('tree_string', models.CharField(max_length=1024)),
                ('similar_cards', models.CharField(default='this', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.CharField(max_length=1024, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='sentence',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='lang_app.Sentence'),
        ),
    ]