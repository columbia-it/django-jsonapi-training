# Generated by Django 2.1.3 on 2018-12-06 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_person'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
