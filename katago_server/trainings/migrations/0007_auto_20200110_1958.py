# Generated by Django 3.0.1 on 2020-01-10 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0006_auto_20200108_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='log_gamma_uncertainty',
            field=models.FloatField(blank=True, null=True, verbose_name='log gamma uncertainty'),
        ),
    ]