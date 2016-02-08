# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_proctoring', '0004_auto_20160208_0727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proctoredexamsoftwaresecurecomment',
            name='stop_time',
            field=models.BigIntegerField(),
        ),
    ]
