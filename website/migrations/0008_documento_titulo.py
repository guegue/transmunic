# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20150324_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='titulo',
            field=models.CharField(default=1, max_length=120),
            preserve_default=False,
        ),
    ]
