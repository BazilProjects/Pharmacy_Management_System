# Generated by Django 3.2 on 2024-10-29 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0015_auto_20241027_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bossed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pharmacy_boss', to='pharmacy.pharmacy'),
        ),
    ]
