# Generated by Django 4.2.16 on 2024-11-27 08:13

from django.db import migrations, models
import django.db.models.deletion

def create_default_contact_relations(apps, schema_editor):
    # Obtener el modelo MedicalCondition
    MedicalCondition = apps.get_model('crm', 'ContactRelation')
    
    # Crear los registros "Mother" y "None" si no existen
    MedicalCondition.objects.get_or_create(name="Mother")
    MedicalCondition.objects.get_or_create(name="Father")

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_rename_medical_comdition_member_medical_condition_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Relation Name')),
            ],
        ),
        migrations.AlterField(
            model_name='membercontact',
            name='relation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.contactrelation'),
        ),
        migrations.RunPython(create_default_contact_relations),
    ]
