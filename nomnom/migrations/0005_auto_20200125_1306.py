# Generated by Django 3.0.1 on 2020-01-25 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nomnom', '0004_auto_20200125_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientset',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nomnom.Recipe'),
        ),
    ]
