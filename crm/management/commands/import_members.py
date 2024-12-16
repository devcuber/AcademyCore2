import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from crm.models import DiscoverySource, MedicalCondition, Member, MemberContact, ContactRelation

class Command(BaseCommand):
    help = "Import members from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file to import.")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        self.import_members(csv_file)

    def import_members(self, csv_file):
        try:
            df = self.read_csv_file(csv_file)
            self.validate_columns(df)
            self.convert_date_format(df)  # Convertir el formato de fecha
            created_count, updated_count, error_count = self.process_rows(df)
            self.stdout.write(self.style.SUCCESS(
                f"Import completed: {created_count} created, {updated_count} updated, {error_count} errors."
            ))
        except (FileNotFoundError, CommandError) as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))

    def read_csv_file(self, csv_file):
        """Reads the CSV file and returns a DataFrame."""
        try:
            self.stdout.write(self.style.NOTICE("Reading CSV file..."))
            df = pd.read_csv(csv_file)
            return df
        except FileNotFoundError:
            raise CommandError(f"File '{csv_file}' does not exist.")
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

    def validate_columns(self, df):
        """Validates that the DataFrame contains the required columns."""
        required_columns = {
            "codigo", "apellido1", "apellido2", "nombre", "curp", "fecha_inscripcion", "nacimiento", "genero",
            "telefono", "correo", "producto", "descubrimiento", "descubrimiento_detalles", 
            "condicion_medica", "condicion_medica_detalles", "estatus", 
            "contacto_principal_nombre", "contacto_principal_relacion", "contacto_principal_telefono",
            "contacto_emergencia_nombre", "contacto_emergencia_relacion", "contacto_emergencia_telefono",
            "contacto_3_nombre", "contacto_3_relacion", "contacto_3_telefono",
            "contacto_4_nombre", "contacto_4_relacion", "contacto_4_telefono",
            "contacto_5_nombre", "contacto_5_telefono"
        }
        if not required_columns.issubset(df.columns):
            raise CommandError(f"The CSV file must contain the following columns: {required_columns}")

    def convert_date_format(self, df):
        """Convert date columns to the required format YYYY-MM-DD."""
        try:
            df['fecha_inscripcion'] = pd.to_datetime(df['fecha_inscripcion'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
            df['nacimiento'] = pd.to_datetime(df['nacimiento'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        except Exception as e:
            raise CommandError(f"Error converting date format: {e}")

    def process_rows(self, df):
        """Processes each row of the DataFrame to create or update members."""
        created_count = 0
        updated_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                discovery_source = self.get_or_create_discovery_source(row['descubrimiento'])
                member, created = Member.objects.update_or_create(
                    member_code=row['codigo'],
                    defaults={
                        "last_name": row['apellido1'],
                        "second_last_name": row['apellido2'],
                        "name": row['nombre'],
                        "curp": row['curp'],
                        "enrollment_date": row['fecha_inscripcion'],
                        "birth_date": row['nacimiento'],
                        "gender": row['genero'],
                        "phone_number": row['telefono'],
                        "email": row['correo'],
                        "how_did_you_hear": discovery_source,
                        "how_did_you_hear_details": row['descubrimiento_detalles'],
                        "medical_condition_details": row['condicion_medica_detalles'],
                    }
                )

                # Eliminar contactos existentes para evitar duplicados
                MemberContact.objects.filter(member=member).delete()

                # Eliminar condiciones médicas existentes
                member.medical_conditions.clear()

                # Añadir la condición médica
                medical_condition = self.get_or_create_medical_condition(row['condicion_medica'])
                member.medical_conditions.add(medical_condition)

                self.create_contacts(member, row)

                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row {index + 1} (codigo {row['codigo']}): {e}"))
                error_count += 1

        return created_count, updated_count, error_count

    def get_or_create_relation(self, relation_name):
        """Gets or creates a ContactRelation instance."""
        relation, _ = ContactRelation.objects.get_or_create(name=relation_name)
        return relation

    def get_or_create_discovery_source(self, source_name):
        """Gets or creates a DiscoverySource instance."""
        discovery_source, _ = DiscoverySource.objects.get_or_create(name=source_name)
        return discovery_source

    def get_or_create_medical_condition(self, condition_name):
        """Gets or creates a MedicalCondition instance."""
        medical_condition, _ = MedicalCondition.objects.get_or_create(name=condition_name)
        return medical_condition

    def create_contact(self, member, name, relation_name, phone_number, is_primary=False, is_emergency=False):
        """Creates or updates a MemberContact instance."""
        relation = self.get_or_create_relation(relation_name)
        MemberContact.objects.update_or_create(
            member=member,
            name=name,
            relation=relation,
            defaults={
                "phone_number": phone_number,
                "is_primary": is_primary,
                "is_emergency": is_emergency,
            }
        )

    def create_contacts(self, member, row):
        """Creates or updates contacts for a member."""
        # Crear contactos principales y de emergencia
        self.create_contact(
            member,
            row['contacto_principal_nombre'],
            row['contacto_principal_relacion'],
            row['contacto_principal_telefono'],
            is_primary=True,
            is_emergency=False
        )

        self.create_contact(
            member,
            row['contacto_emergencia_nombre'],
            row['contacto_emergencia_relacion'],
            row['contacto_emergencia_telefono'],
            is_primary=False,
            is_emergency=True
        )

        # Crear contactos adicionales
        for i in range(3, 6):
            contact_name = row.get(f'contacto_{i}_nombre')
            contact_relation = row.get(f'contacto_{i}_relacion')
            contact_phone = row.get(f'contacto_{i}_telefono')
            if contact_name and contact_relation and contact_phone:
                self.create_contact(
                    member,
                    contact_name,
                    contact_relation,
                    contact_phone,
                    is_primary=False,
                    is_emergency=False
                )
