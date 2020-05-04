# Generated by Django 3.0.5 on 2020-05-04 03:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0006_auto_20200504_0205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=128, validators=[django.core.validators.RegexValidator('^[-0-9a-zA-Z]*$', 'Only alphanumeric or dash characters are allowed.')], verbose_name='neural network name'),
        ),
        migrations.AlterField(
            model_name='network',
            name='parent_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='variants', to='trainings.Network', verbose_name='Parent network for BayesElo prior'),
        ),
    ]
