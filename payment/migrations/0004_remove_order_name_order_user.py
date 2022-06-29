# Generated by Django 4.0.5 on 2022-06-29 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairbet_auth_app', '0002_alter_profile_id'),
        ('payment', '0003_order_created_order_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='name',
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fairbet_auth_app.profile'),
        ),
    ]
