# Generated by Django 4.2 on 2023-05-27 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0018_assetitems_count_assetitems_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetitems',
            name='price',
            field=models.FloatField(default=0, verbose_name='السعر'),
        ),
    ]
