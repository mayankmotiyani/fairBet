# Generated by Django 4.0.5 on 2022-07-06 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fairbet_auth_app', '0002_alter_profile_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['created']},
        ),
    ]
