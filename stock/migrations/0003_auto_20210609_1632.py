# Generated by Django 3.2.3 on 2021-06-09 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20210530_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='industry',
            field=models.CharField(default='0', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stock',
            name='market',
            field=models.CharField(default='0', max_length=30),
            preserve_default=False,
        ),
    ]