# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_banner_vertical'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField(null=True, verbose_name=b'fecha', blank=True)),
                ('archivo', models.FileField(null=True, upload_to=b'documentos', blank=True)),
            ],
            options={
                'verbose_name': 'Documentos',
                'verbose_name_plural': 'Documentos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=120)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
            ],
            options={
                'verbose_name': 'Tipo',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo',
            field=models.ForeignKey(related_name='Tipo', to='website.TipoDoc'),
            preserve_default=True,
        ),
    ]
