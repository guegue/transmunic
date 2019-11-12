# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0007_auto_20150219_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.CharField(max_length=500, null=True, blank=True)),
                ('enlace', models.CharField(max_length=200, null=True, blank=True)),
                ('orden', models.IntegerField(null=True, blank=True)),
                ('imagen', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'banner', blank=True)),
                ('municipio', models.ForeignKey(to='lugar.Municipio')),
            ],
            options={
                'ordering': ['orden'],
            },
            bases=(models.Model,),
        ),
    ]
