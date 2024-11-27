# Generated by Django 4.2.16 on 2024-11-22 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0002_rename_customer_memberaccesslog_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preregister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('curp', models.CharField(max_length=18, unique=True)),
                ('birth_date', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('photo', models.ImageField(upload_to='members_photos/')),
                ('how_did_you_hear_details', models.CharField(blank=True, max_length=255, null=True)),
                ('has_illness', models.BooleanField(default=False, verbose_name='Has any illness')),
                ('has_allergy', models.BooleanField(default=False, verbose_name='Has any allergy')),
                ('has_flat_feet', models.BooleanField(default=False, verbose_name='Has flat feet')),
                ('has_heart_conditions', models.BooleanField(default=False, verbose_name='Has heart conditions')),
                ('how_did_you_hear', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discovery_sources', to='crm.discoverysource')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member', to='crm.member')),
            ],
        ),
    ]