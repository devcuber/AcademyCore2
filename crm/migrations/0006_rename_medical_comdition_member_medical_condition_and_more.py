# Generated by Django 4.2.16 on 2024-11-27 06:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_medicalcondition_member_medical_comdition_details_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='medical_comdition',
            new_name='medical_condition',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='medical_comdition_details',
            new_name='medical_condition_details',
        ),
    ]
