# Generated by Django 2.1 on 2018-08-10 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps_main', '0002_remove_address_google_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='fusion_table_id',
            new_name='fusion_table',
        ),
        migrations.RenameField(
            model_name='fusiontable',
            old_name='google_user_id',
            new_name='google_user',
        ),
    ]