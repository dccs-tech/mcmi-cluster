# Generated by Django 3.0 on 2020-06-16 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subnet', '0005_auto_20190526_1431'),
        ('storage', '0002_auto_20190406_2145'),
        ('storage_mount', '0004_auto_20200605_1459'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='storagemount',
            unique_together={('subnet', 'name'), ('storage', 'name')},
        ),
    ]