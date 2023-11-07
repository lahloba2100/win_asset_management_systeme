# Generated by Django 4.2.1 on 2023-05-20 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0011_discounttax'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetinvoice',
            name='discount_tax',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='add_asset_invoice.discounttax', verbose_name='ضريبة الخصم'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='addition_tax',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='add_asset_invoice.additiontax', verbose_name='ضريبة الاضافة'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='tax_decrease',
            field=models.FloatField(blank=True, null=True, verbose_name='ضريبة الخصم'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='tax_increase',
            field=models.FloatField(blank=True, null=True, verbose_name='ضريبة الاضافة'),
        ),
    ]
