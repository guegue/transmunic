# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-21 20:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0001_initial'),
        #('core', '0010_merge_20200121_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transferencia',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('anio', models.IntegerField(verbose_name='A\xf1o')),
                ('periodo', models.CharField(max_length=1)),
                ('corriente', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital', models.DecimalField(decimal_places=2, max_digits=12)),
                ('departamento', models.ForeignKey(null=True,
                                                   on_delete=django.db.models.deletion.CASCADE, to='lugar.Departamento')),
                ('municipio', models.ForeignKey(blank=True, null=True,
                                                on_delete=django.db.models.deletion.CASCADE, to='lugar.Municipio')),
            ],
            options={
                'ordering': ['anio', 'periodo', 'municipio'],
                'verbose_name': 'Transferencia',
                'verbose_name_plural': 'Transferencias',
            },
        ),
        migrations.AlterUniqueTogether(
            name='transferencia',
            unique_together=set([('anio', 'periodo', 'municipio')]),
        ),
    ]