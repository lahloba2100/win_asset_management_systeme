# Generated by Django 4.2 on 2023-05-27 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0019_alter_assetitems_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetitems',
            name='count',
            field=models.DecimalField(decimal_places=4, default=1, max_digits=4, verbose_name='عدد'),
        ),
    ]
