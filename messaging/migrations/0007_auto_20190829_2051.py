# Generated by Django 2.1.5 on 2019-08-29 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0006_messagethread_psk'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagethread',
            name='admin',
            field=models.CharField(default='admin', max_length=32),
        ),
        migrations.AddField(
            model_name='messagethread',
            name='friend1',
            field=models.CharField(default='friend1', max_length=32),
        ),
    ]