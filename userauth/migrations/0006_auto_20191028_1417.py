# Generated by Django 2.1.5 on 2019-10-28 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0005_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='channel_layer',
            field=models.CharField(default='ch', max_length=80),
        ),
        migrations.AddField(
            model_name='user',
            name='channel_name',
            field=models.CharField(default='ch', max_length=80),
        ),
    ]
