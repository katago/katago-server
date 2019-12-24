# Generated by Django 2.2.8 on 2019-12-24 00:11

from django.db import migrations, models
import katago_server.games.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rules', models.CharField(choices=[('Japanese', 'JAPANESE'), ('Chinese', 'CHINESE'), ('Trump Taylor', 'TROMP_TAYLOR')], default=katago_server.games.models.GamesRulesType('Chinese'), max_length=20)),
                ('handicap', models.IntegerField(default=0)),
                ('komi', models.DecimalField(decimal_places=1, default=7.0, max_digits=3)),
                ('result', models.CharField(choices=[('W', 'WHITE'), ('B', 'BLACK'), ('0', 'JIGO'), ('∅', 'MOSHOUBOU')], max_length=15)),
                ('score', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
            options={
                'verbose_name_plural': 'Matches',
            },
        ),
        migrations.CreateModel(
            name='SelfPlay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rules', models.CharField(choices=[('Japanese', 'JAPANESE'), ('Chinese', 'CHINESE'), ('Trump Taylor', 'TROMP_TAYLOR')], default=katago_server.games.models.GamesRulesType('Chinese'), max_length=20)),
                ('handicap', models.IntegerField(default=0)),
                ('komi', models.DecimalField(decimal_places=1, default=7.0, max_digits=3)),
                ('result', models.CharField(choices=[('W', 'WHITE'), ('B', 'BLACK'), ('0', 'JIGO'), ('∅', 'MOSHOUBOU')], max_length=15)),
                ('score', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
