# Generated by Django 2.1.5 on 2019-08-26 20:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_message_old'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message_old',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='message_old',
            name='thread',
        ),
        migrations.DeleteModel(
            name='Message_Old',
        ),
    ]
