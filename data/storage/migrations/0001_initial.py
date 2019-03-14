# Generated by Django 2.1.7 on 2019-03-14 02:31

from django.db import migrations, models
import django.db.models.deletion
import systems.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('network', '0001_initial'),
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('created', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(null=True)),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('config', systems.models.fields.EncryptedDataField(default={})),
                ('type', models.CharField(max_length=128, null=True)),
                ('variables', systems.models.fields.EncryptedDataField(default={})),
                ('state_config', systems.models.fields.EncryptedDataField(default={})),
                ('groups', models.ManyToManyField(related_name='storage_relation', to='group.Group')),
                ('network', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='storage_relation', to='network.Network')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='storage',
            unique_together={('network', 'name')},
        ),
    ]
