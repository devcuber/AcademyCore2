# Generated by Django 4.2.16 on 2024-12-05 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0008_remove_member_has_allergy_and_more'),
        ('preregistration', '0009_remove_preregister_has_allergy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='preregister',
            name='medical_conditions',
            field=models.ManyToManyField(blank=True, to='crm.medicalcondition'),
        ),
    ]
