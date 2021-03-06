# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DnsRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('name', models.CharField(default=b'@', max_length=200)),
                ('value', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='DomainRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('comment', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RedirectRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=b'/', max_length=200)),
                ('value', models.CharField(max_length=200)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iebu.DomainRecord')),
            ],
        ),
        migrations.AddField(
            model_name='domainrecord',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iebu.Folder'),
        ),
        migrations.AddField(
            model_name='domainrecord',
            name='main_a_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iebu.DnsRecord'),
        ),
        migrations.AddField(
            model_name='dnsrecord',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iebu.DomainRecord'),
        ),
    ]
