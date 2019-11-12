# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_documento_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='imagen',
            field=sorl.thumbnail.fields.ImageField(null=True, upload_to=b'documento', blank=True),
            preserve_default=True,
        ),
    ]
