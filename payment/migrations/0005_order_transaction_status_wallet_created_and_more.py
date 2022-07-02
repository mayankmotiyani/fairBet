# Generated by Django 4.0.5 on 2022-07-02 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_remove_order_name_order_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='transaction_status',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='transactionStatus'),
        ),
        migrations.AddField(
            model_name='wallet',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]