# Generated by Django 2.2 on 2019-05-14 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_server_ssh_port'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='backup_device',
        ),
        migrations.RemoveField(
            model_name='server',
            name='data_device',
        ),
    ]
