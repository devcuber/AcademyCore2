# Generated by Django 4.2.16 on 2024-11-27 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preregistration', '0002_alter_preregister_how_did_you_hear'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preregister',
            name='folio',
            field=models.CharField(blank=True, editable=False, max_length=100, unique=True),
        ),
    ]
