# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2018-09-17 16:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_call_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='call',
            name='files',
        ),
        migrations.AddField(
            model_name='file',
            name='callId',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.Call'),
        ),
    ]