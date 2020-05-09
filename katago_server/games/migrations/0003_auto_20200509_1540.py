# Generated by Django 3.0.5 on 2020-05-09 15:40

import django.core.files.storage
from django.db import migrations, models
import katago_server.contrib.validators
import katago_server.games.models.abstract_game
import katago_server.games.models.training_game


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20200509_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratinggame',
            name='sgf_file',
            field=models.FileField(max_length=200, storage=django.core.files.storage.FileSystemStorage(location='/data/games'), upload_to=katago_server.games.models.abstract_game.upload_sgf_to, validators=[katago_server.contrib.validators.FileValidator(max_size=524288)], verbose_name='SGF file'),
        ),
        migrations.AlterField(
            model_name='traininggame',
            name='sgf_file',
            field=models.FileField(max_length=200, storage=django.core.files.storage.FileSystemStorage(location='/data/games'), upload_to=katago_server.games.models.abstract_game.upload_sgf_to, validators=[katago_server.contrib.validators.FileValidator(max_size=524288)], verbose_name='SGF file'),
        ),
        migrations.AlterField(
            model_name='traininggame',
            name='training_data_file',
            field=models.FileField(max_length=200, storage=django.core.files.storage.FileSystemStorage(location='/data/training_npz'), upload_to=katago_server.games.models.training_game.upload_training_data_to, validators=[katago_server.contrib.validators.FileValidator(content_types=('application/zip',), max_size=314572800)], verbose_name='training data (npz)'),
        ),
    ]
