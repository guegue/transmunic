# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150807_1106'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subsubtipoingreso',
            options={'ordering': ['codigo'], 'verbose_name_plural': 'Sub-subtipos de ingresos'},
        ),
        migrations.AlterModelOptions(
            name='subtipoingreso',
            options={'ordering': ['codigo'], 'verbose_name_plural': 'Subtipos de ingresos'},
        ),
        migrations.AlterModelOptions(
            name='tipogasto',
            options={'ordering': ['codigo'], 'verbose_name_plural': 'Tipo de gastos'},
        ),
        migrations.AlterModelOptions(
            name='tipoingreso',
            options={'ordering': ['codigo'], 'verbose_name_plural': 'Tipo de ingreso'},
        ),
        migrations.AddField(
            model_name='anio',
            name='actualizado',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anio',
            name='final',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anio',
            name='inicial',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='ficha',
            field=models.FileField(null=True, upload_to=b'proyecto', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversion',
            name='nombremunic',
            field=models.CharField(max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='catinversion',
            field=models.ForeignKey(related_name='categoria_inversion', blank=True, to='core.CatInversion', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='tipoproyecto',
            field=models.ForeignKey(related_name='tipo_proyecto', blank=True, to='core.TipoProyecto', null=True),
            preserve_default=True,
        ),
    ]
