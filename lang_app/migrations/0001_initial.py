# Generated by Django 2.1 on 2018-11-01 15:48

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
                ('chunk_tree_string', models.CharField(max_length=1024)),
                ('similar_cards', models.CharField(default=None, max_length=128, null=True)),
                ('question_tree_string', models.CharField(default=None, max_length=1024, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.CharField(max_length=1024, unique=True)),
                ('sentence_tree_string', models.CharField(default=None, max_length=1024)),
                ('uncommon_words_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='sentence',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='lang_app.Sentence'),
        ),
    ]
