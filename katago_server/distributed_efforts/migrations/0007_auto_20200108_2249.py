# Generated by Django 3.0.1 on 2020-01-08 22:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributed_efforts', '0006_auto_20200104_0247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='board_size_x',
        ),
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='board_size_y',
        ),
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='game_extra_params',
        ),
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='handicap',
        ),
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='komi',
        ),
        migrations.RemoveField(
            model_name='rankingestimationgamedistributedtask',
            name='rules_params',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='board_size_x',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='board_size_y',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='game_extra_params',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='handicap',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='komi',
        ),
        migrations.RemoveField(
            model_name='traininggamedistributedtask',
            name='rules_params',
        ),
    ]
