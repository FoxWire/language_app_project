# Generated by Django 2.1 on 2018-11-26 18:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_type', models.CharField(max_length=1024)),
                ('next_block', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lang_app.Block')),
            ],
        ),
        migrations.CreateModel(
            name='QandA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(default=None, max_length=1024, null=True)),
                ('answer_correct', models.BooleanField(default=None, null=True)),
                ('block', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qandas', to='lang_app.Block')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
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
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_id', models.IntegerField(default=None)),
                ('session_size', models.IntegerField(default=2)),
                ('current_block', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_block', to='lang_app.Block')),
            ],
        ),
        migrations.CreateModel(
            name='UserState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_size', models.IntegerField(default=3)),
                ('current_policy_id', models.IntegerField(default=None)),
                ('policy_ids', models.CharField(default='123', max_length=1024)),
                ('current_session', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_session', to='lang_app.Session')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='user_state',
            field=models.ForeignKey(on_delete=None, to='lang_app.UserState'),
        ),
        migrations.AddField(
            model_name='question',
            name='sentence',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='lang_app.Sentence'),
        ),
        migrations.AddField(
            model_name='qanda',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lang_app.Question'),
        ),
        migrations.AddField(
            model_name='block',
            name='session',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='lang_app.Session'),
        ),
    ]
