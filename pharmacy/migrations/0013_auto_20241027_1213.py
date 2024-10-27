# Generated by Django 3.2 on 2024-10-27 12:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0012_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmacy',
            name='is_supervised_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='super_vising_pharmacist', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='user_profile/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('salesperson', 'Salesperson'), ('manager', 'Manager'), ('cashier', 'Cashier'), ('supervising_pharmacist', 'Supervising_Pharmacist')], max_length=25),
        ),
    ]
