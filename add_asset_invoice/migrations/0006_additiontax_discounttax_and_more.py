# Generated by Django 4.2 on 2023-05-19 02:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0005_assetgroup_alter_assetitems_asset_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addition_tax', models.CharField(max_length=100, verbose_name='ضريبة الاضافة')),
                ('percent_addition_tax', models.FloatField(blank=True, null=True, verbose_name='نسبة الضريبة')),
                ('value_addition_tax', models.FloatField(blank=True, null=True, verbose_name='قيمة الضريبة')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_tax', models.CharField(max_length=100, verbose_name='ضريبة الخصم')),
                ('percent_discount_tax', models.FloatField(blank=True, null=True, verbose_name='نسبة الضريبة')),
                ('value_discount_tax', models.FloatField(blank=True, null=True, verbose_name='قيمة الضريبة')),
            ],
        ),
        migrations.RemoveField(
            model_name='assetinvoice',
            name='tax_increase',
        ),
        migrations.AddField(
            model_name='assetinvoice',
            name='addition_tax',
            field=models.ForeignKey(default=14, on_delete=django.db.models.deletion.PROTECT, to='add_asset_invoice.additiontax', verbose_name='ضريبة الزيادة '),
            preserve_default=False,
        ),
    ]
