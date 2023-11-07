# Generated by Django 4.2 on 2023-07-03 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('add_asset_invoice', '0040_alter_destruction_destruction_percent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destruction',
            name='destruction_percent',
            field=models.FloatField(blank=True, null=True, verbose_name='نسبة الاهلاك'),
        ),
        migrations.AlterField(
            model_name='destruction',
            name='destruction_value',
            field=models.FloatField(blank=True, null=True, verbose_name='قيمة الاهلاك'),
        ),
    ]
