# Generated by Django 3.0.1 on 2020-01-25 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nomnom', '0002_auto_20200117_1952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientset',
            old_name='name',
            new_name='ingredient',
        ),
    ]
