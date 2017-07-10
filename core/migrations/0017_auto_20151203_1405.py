# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20151203_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organizacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('correo', models.CharField(max_length=100, null=True, blank=True)),
                ('web', models.CharField(max_length=200, null=True, blank=True)),
                ('logo', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'organizacion', blank=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Organizaciones',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='areageografica',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'U', b'Urbana'), (b'R', b'Rural'), (b'O', b'Otros')]),
            preserve_default=True,
        ),
    ]
