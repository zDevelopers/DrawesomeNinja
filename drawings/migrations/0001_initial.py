# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-12 11:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drawer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='members.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='DrawingRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=16)),
                ('drawers', models.ManyToManyField(to='drawings.Drawer')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='WordsList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=256)),
                ('public', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drawings.Drawer')),
                ('words', models.ManyToManyField(to='drawings.Word')),
            ],
        ),
        migrations.AddField(
            model_name='drawingroom',
            name='words_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='drawings.WordsList'),
        ),
    ]
