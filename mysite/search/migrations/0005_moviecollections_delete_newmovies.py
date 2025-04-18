# Generated by Django 5.1.7 on 2025-04-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_cachedmovies'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieCollections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic_name', models.CharField(max_length=20)),
                ('movies_list', models.JSONField()),
            ],
        ),
        migrations.DeleteModel(
            name='newMovies',
        ),
    ]
