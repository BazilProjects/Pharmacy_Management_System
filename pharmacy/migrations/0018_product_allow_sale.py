# Generated by Django 3.2 on 2024-10-30 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0017_auto_20241030_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='allow_sale',
            field=models.BooleanField(default=True),
        ),
    ]
