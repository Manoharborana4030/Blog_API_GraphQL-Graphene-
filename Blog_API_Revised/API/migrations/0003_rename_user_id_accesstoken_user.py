# Generated by Django 3.2.13 on 2022-05-31 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0002_accesstoken'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accesstoken',
            old_name='user_id',
            new_name='user',
        ),
    ]
