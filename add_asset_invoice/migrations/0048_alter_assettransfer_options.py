# Generated by Django 4.2 on 2023-07-13 00:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0047_rename_asset_id_assettransfer_asset_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assettransfer',
            options={'verbose_name': 'تحويل أصل', 'verbose_name_plural': 'تحويلات أصول'},
        ),
    ]
