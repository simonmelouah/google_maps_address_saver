# Generated by Django 2.1 on 2018-08-09 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps_main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='google_user_id',
        ),
    ]