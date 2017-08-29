# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=200)),
                ('sub_domain', models.CharField(max_length=100)),
                ('last_download_date', models.DateField()),
                ('category_synced', models.BooleanField(default=False)),
            ],
        ),
    ]
