# Generated by Django 3.0.1 on 2020-01-03 17:40

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import katago_server.contrib.validators
import katago_server.trainings.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('nb_blocks', models.IntegerField()),
                ('nb_channels', models.IntegerField()),
                ('model_architecture_details', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('model_file', models.FileField(upload_to=katago_server.trainings.models.upload_network_to, validators=[katago_server.contrib.validators.FileValidator(content_types=('application/gzip',), max_size=314572800)])),
                ('ranking_value', models.DecimalField(decimal_places=2, max_digits=7)),
                ('ranking_stdev', models.DecimalField(decimal_places=2, max_digits=7)),
            ],
        ),
    ]
