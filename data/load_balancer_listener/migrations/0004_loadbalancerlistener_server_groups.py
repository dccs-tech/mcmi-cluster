# Generated by Django 3.0 on 2020-07-12 03:17

from django.db import migrations
import systems.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('load_balancer_listener', '0003_auto_20200605_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadbalancerlistener',
            name='server_groups',
            field=systems.models.fields.CSVField(null=True),
        ),
    ]