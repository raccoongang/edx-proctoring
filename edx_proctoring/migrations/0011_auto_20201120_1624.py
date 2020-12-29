# Generated by Django 2.2.16 on 2020-11-20 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_proctoring', '0010_update_backend'),
    ]

    operations = [
        migrations.AddField(
            model_name='proctoredexamstudentattempt',
            name='exam_grade',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='proctoredexamstudentattempt',
            name='passed',
            field=models.BooleanField(default=False),
        ),
    ]