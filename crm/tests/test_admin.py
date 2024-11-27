from unittest import skip
from django.test import TestCase
from django.contrib.auth.models import User
from crm.models import DiscoverySource, Member, MemberContact

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from crm.admin import MemberAdmin

@skip("Inactivando pruebas de MemberAdminSaveModelTest ya que las reglas con respecto a los contactos han cambiado")
class MemberAdminSaveModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configurar datos iniciales
        cls.factory = RequestFactory()
        cls.site = AdminSite()
        cls.user = User.objects.create_superuser(username="admin", password="adminpassword", email="admin@example.com")
        cls.discovery_source = DiscoverySource.objects.create(name="Social Media")
        cls.member = Member.objects.create(
            member_code="M001",
            name="John Doe",
            curp="JOHN010101HDFRRN09",
            birth_date="1990-01-01",
            gender="M",
            phone_number="+521234567890",
            email="john.doe@example.com",
            how_did_you_hear=cls.discovery_source,
        )
        cls.admin = MemberAdmin(Member, cls.site)

    def test_valid_single_primary_and_emergency_contact(self):
        """Verifica que `save_model` acepte un miembro con exactamente un contacto principal y uno de emergencia."""
        # Crear un contacto relacionado con el miembro
        contact = MemberContact.objects.create(
            member=self.member,
            name="Jane Doe",
            phone_number="+521234567891",
            is_primary=True,
            is_emergency=True,
        )

        # Asociar el contacto al miembro
        self.member.contacts.add(contact, bulk=False)

        # Llamar al método save_model directamente
        self.admin.save_model(request=None, obj=self.member, form=None, change=False)

        # Validar los contactos después de guardar
        primary_contacts = self.member.contacts.filter(is_primary=True)
        emergency_contacts = self.member.contacts.filter(is_emergency=True)

        # Validaciones
        self.assertEqual(primary_contacts.count(), 1, "Debe haber exactamente un contacto principal.")
        self.assertEqual(emergency_contacts.count(), 1, "Debe haber exactamente un contacto de emergencia.")
        self.assertEqual(
            primary_contacts.first(),
            emergency_contacts.first(),
            "El contacto principal y de emergencia pueden ser el mismo.",
        )

    def test_multiple_primary_contacts_not_allowed(self):
        """Verifica que no se permitan múltiples contactos principales para un miembro."""
        # Crear dos contactos principales
        MemberContact.objects.create(
            member=self.member,
            name="Contact 1",
            phone_number="+521234567891",
            is_primary=True,
        )
        MemberContact.objects.create(
            member=self.member,
            name="Contact 2",
            phone_number="+521234567892",
            is_primary=True,
        )

        # Llamar al método save_model y esperar un ValueError
        with self.assertRaises(ValueError, msg="No se debe permitir más de un contacto principal."):
            self.admin.save_model(request=None, obj=self.member, form=None, change=False)

    def test_multiple_emergency_contacts_not_allowed(self):
        """Verifica que no se permitan múltiples contactos de emergencia para un miembro."""
        # Crear dos contactos de emergencia
        MemberContact.objects.create(
            member=self.member,
            name="Emergency Contact 1",
            phone_number="+521234567891",
            is_emergency=True,
        )
        MemberContact.objects.create(
            member=self.member,
            name="Emergency Contact 2",
            phone_number="+521234567892",
            is_emergency=True,
        )

        # Llamar al método save_model y esperar un ValueError
        with self.assertRaises(ValueError, msg="No se debe permitir más de un contacto de emergencia."):
            self.admin.save_model(request=None, obj=self.member, form=None, change=False)

    def test_must_have_exactly_one_primary_contact(self):
        """Verifica que debe existir exactamente un contacto principal para un miembro."""
        # No crear ningún contacto principal
        MemberContact.objects.create(
            member=self.member,
            name="Jane Doe",
            phone_number="+521234567891",
            is_emergency=True,
        )

        # Llamar al método save_model y esperar un ValueError
        with self.assertRaises(ValueError, msg="Debe haber exactamente un contacto principal."):
            self.admin.save_model(request=None, obj=self.member, form=None, change=False)

    def test_must_have_exactly_one_emergency_contact(self):
        """Verifica que debe existir exactamente un contacto de emergencia para un miembro."""
        # No crear ningún contacto de emergencia
        MemberContact.objects.create(
            member=self.member,
            name="Jane Doe",
            phone_number="+521234567891",
            is_primary=True,
        )

        # Llamar al método save_model y esperar un ValueError
        with self.assertRaises(ValueError, msg="Debe haber exactamente un contacto de emergencia."):
            self.admin.save_model(request=None, obj=self.member, form=None, change=False)

    def test_contact_can_be_primary_and_emergency(self):
        """Verifica que un contacto puede ser tanto principal como de emergencia."""
        # Crear un contacto que sea principal y de emergencia
        MemberContact.objects.create(
            member=self.member,
            name="Jane Doe",
            phone_number="+521234567891",
            is_primary=True,
            is_emergency=True,
        )

        # Llamar al método save_model directamente
        self.admin.save_model(request=None, obj=self.member, form=None, change=False)

        primary_contacts = self.member.contacts.filter(is_primary=True)
        emergency_contacts = self.member.contacts.filter(is_emergency=True)

        # Validaciones
        self.assertEqual(primary_contacts.count(), 1, "Debe haber exactamente un contacto principal.")
        self.assertEqual(emergency_contacts.count(), 1, "Debe haber exactamente un contacto de emergencia.")
        self.assertEqual(
            primary_contacts.first(),
            emergency_contacts.first(),
            "El contacto principal y de emergencia pueden ser el mismo.",
        )
