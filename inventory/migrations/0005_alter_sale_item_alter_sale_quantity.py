# Generated by Django 4.2 on 2025-04-06 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_sale_item_sale_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.item'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sale',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
