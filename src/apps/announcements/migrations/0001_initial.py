# Generated by Django 3.0.11 on 2021-01-18 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='updated date')),
                ('title', models.CharField(db_index=True, help_text='Title of the announcement section.', max_length=240, unique=True, verbose_name='title')),
                ('contents', models.TextField(blank=True, help_text='HTML contents of the announcement section.', verbose_name='contents')),
                ('display_order', models.IntegerField(db_index=True, help_text='Order of sections. Smaller indices come first.', unique=True, verbose_name='display_order')),
                ('enabled', models.BooleanField(db_index=True, default=True, help_text='Enable for display on front page?', verbose_name='enabled')),
                ('notes', models.TextField(blank=True, help_text='Private notes about this announcement', max_length=1024, verbose_name='notes')),
            ],
            options={
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'ordering': ['-display_order'],
            },
        ),
    ]
