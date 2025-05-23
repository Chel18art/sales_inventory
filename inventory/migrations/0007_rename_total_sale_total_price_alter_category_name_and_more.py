# Generated by Django 4.2 on 2025-04-06 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_category_name_alter_item_category_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='total',
            new_name='total_price',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
