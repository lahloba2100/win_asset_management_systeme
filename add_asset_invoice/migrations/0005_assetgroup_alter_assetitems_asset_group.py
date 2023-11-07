# Generated by Django 4.2 on 2023-05-13 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0004_assetinvoice_invoice_pdf_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_group', models.CharField(max_length=100, verbose_name='مجموعة الاصل')),
            ],
        ),
        migrations.AlterField(
            model_name='assetitems',
            name='asset_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='add_asset_invoice.assetgroup', verbose_name='مجموعة الاصل'),
        ),
    ]
