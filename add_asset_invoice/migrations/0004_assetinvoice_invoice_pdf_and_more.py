# Generated by Django 4.2 on 2023-05-13 03:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0003_alter_assetinvoice_invoice_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetinvoice',
            name='invoice_pdf',
            field=models.FileField(blank=True, null=True, upload_to='invoices/'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='amount_paid',
            field=models.FloatField(blank=True, null=True, verbose_name='المدفوع '),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='invoice_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='تاريخ الفاتورة'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='رقم الفاتورة'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='remaining_balance',
            field=models.FloatField(blank=True, null=True, verbose_name='المتبقي '),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='supplier_address',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='عنوان المورد'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='supplier_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم المورد'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='supplier_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='تليفون المورد'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='tax_decrease',
            field=models.FloatField(blank=True, null=True, verbose_name='ضريبة بالنقص'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='tax_increase',
            field=models.FloatField(blank=True, null=True, verbose_name='ضريبة بالزيادة'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='total_invoice_cost',
            field=models.FloatField(blank=True, null=True, verbose_name='اجمالي الفاتورة'),
        ),
        migrations.AlterField(
            model_name='assetinvoice',
            name='transportation_cost',
            field=models.FloatField(blank=True, null=True, verbose_name='تكلفة النقل'),
        ),
    ]
