# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0003_auto_20141210_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='clasificacionmunic',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2015, 2, 19, 21, 27, 20, 272331, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
