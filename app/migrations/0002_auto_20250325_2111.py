# Generated by Django 2.2.28 on 2025-03-25 18:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-posted'], 'verbose_name': 'Статья блога', 'verbose_name_plural': 'статьи блога'},
        ),
        migrations.AlterField(
            model_name='blog',
            name='posted',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2025, 3, 25, 21, 11, 7, 579902), verbose_name='Опубликована'),
        ),
        migrations.AlterModelTable(
            name='blog',
            table='Posts',
        ),
    ]
