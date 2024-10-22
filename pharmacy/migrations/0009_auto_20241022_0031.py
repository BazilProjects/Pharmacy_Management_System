# Generated by Django 3.2 on 2024-10-22 00:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0008_auto_20241014_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='product',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='quantity',
        ),
        migrations.AddField(
            model_name='sale',
            name='transaction_hash',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.CreateModel(
            name='SaleProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pharmacy.product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.sale')),
            ],
        ),
    ]
