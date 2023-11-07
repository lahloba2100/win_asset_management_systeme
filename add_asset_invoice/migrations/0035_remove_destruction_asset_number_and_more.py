# Generated by Django 4.2 on 2023-06-24 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0034_rename_asset_item_destruction_asset_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='destruction',
            name='asset_number',
        ),
        migrations.AddField(
            model_name='destruction',
            name='asset_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='add_asset_invoice.assetitems', verbose_name='رقم الاصل'),
        ),
    ]
