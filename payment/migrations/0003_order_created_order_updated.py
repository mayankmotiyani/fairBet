# Generated by Django 4.0.5 on 2022-06-29 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]