import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.db import DataError
from django.contrib.auth.models import User
from .models import DiscoverySource, Member, MemberAccessLog, AccessStatus, MemberContact

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from .admin import MemberAdmin



class CustomerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Carga datos iniciales de prueba solo para los status, el usuario y la fuente de descubrimiento"""
        cls.user = User.objects.create_user(username="testuser", password="testpassword")
        cls.discovery_source = DiscoverySource.objects.create(name="Social Media")
        #Los Status se crean en las migraciones

    def create_member(self, **kwargs):
        defaults = {
            "member_code": uuid.uuid4(),
            "name": "Juan Pérez",
            "curp": "JUAP010101HDFRRN09",
            "birth_date": "1985-01-01",
            "gender": "M",
            "phone_number": "+521234567890",
            "email": "juan.perez@example.com",
            "photo": None,
            "how_did_you_hear": self.discovery_source,
            "has_illness": False,
            "has_allergy": False,
            "has_flat_feet": False,
            "has_heart_conditions": False,
        }
        defaults.update(kwargs)
        return Member.objects.create(**defaults)
    
#Test 2 pruebas CURP
#Debe existir el campo CURP y debe ser único, y obligatorio, con el
#propósito de evitar duplicado de alta de clientes
    def test_invalid_curp_formats(self):
        """Verifica que no se permita un CURP con formatos incorrectos."""
        invalid_curps = [
            "INVALID1234", "JUAP010101HDF", "JUAP010101HDFRRRNN",
            "1234567890123456", "JUAP@10101HDFRRN09", ""
        ]
        for curp in invalid_curps:
            with self.assertRaises(ValidationError, msg=f"El CURP {curp} no debería ser válido."):
                member = self.create_member(curp=curp)
                member.full_clean()

    def test_duplicate_curp_not_allowed(self):
        """Verifica que no se pueda insertar otro cliente con un CURP existente."""
        curp = "JUAP010101HDFRRN09"
        self.create_member(curp=curp)
        with self.assertRaises(IntegrityError):
            self.create_member(curp=curp)


    #TEST4 pruebas de cambios de log
    def test_create_member_creates_status_log(self):
        """Valida que al crear un cliente, se registre automáticamente el primer log de estado."""

        # Crear cliente y pasar el usuario si es necesario en el método save
        member = Member.objects.create(
            member_code="CUST0004",
            name="Carlos Hernández",
            curp="CARH010101HDFRRN04",
            birth_date="1985-01-01",
            gender="M",
            phone_number="+521234567890",
            email="carlos.hernandez@example.com",
            how_did_you_hear=self.discovery_source
        )
        #print(f"test_create_member_creates_status_log user: {self.user}")
        member.save(user= self.user)  # Asumiendo que el método `save` maneja la creación del log

        # Verificar que se haya creado un log asociado al cliente
        member_status = MemberAccessLog.objects.filter(member=member).first()

        self.assertIsNotNone(member_status, "No se creó el log de estado al crear el cliente.")
        self.assertEqual(member_status.status.name, "Active", "El estado inicial del cliente no es el esperado.")
        self.assertEqual(member_status.reason, "New member", "La razón del cambio de estado inicial no es la esperada.")
        #TODO
        #self.assertEqual(member_status.changed_by, self.user, "El usuario que cambió el estado no coincide.")

    def test_status_log_cannot_be_modified(self):
        """Valida que no se permita modificar un log de estado una vez creado."""
        # Crear un log de estado inicial
        member =self.create_member(member_code=str(uuid.uuid4()), curp="CARH010101HDFRRN05")
        active_status = AccessStatus.objects.get(name=("Active"))
        inactive_status = AccessStatus.objects.get(name=("Inactive"))
        initial_status_log = MemberAccessLog.objects.create(
            member=member,
            status=active_status,
            reason="Estado inicial",
            changed_by=self.user,
        )
        # Intentar modificar el log de estado
        with self.assertRaises(ValidationError, msg="Debería lanzarse un ValidationError al intentar modificar el log de estado."):
            initial_status_log.status = inactive_status  # Intentar cambiar el estado
            initial_status_log.reason = "Intento de cambio"  # Intentar cambiar la razón
            initial_status_log.save()  # Guardar los cambios


#TEST 5 El sistema validará la información ingresada por el usuario para asegurar
#la precisión y consistencia de los datos, incluyendo la verificación de
#formatos de correo electrónico, números de teléfono válidos, etc.

    def test_invalid_email_formats(self):
        """Valida formatos inválidos de correo electrónico."""
        invalid_emails = [
            "juan.perez@", "juan.perez@com", "@example.com", 
            "juan.perez@@example.com", "juan.perezexample.com", ""
        ]
        curp_prefix  = 'MARH010101HDFRRN'
        curp_suffix = 60

        for email in invalid_emails:
            curp = f"{curp_prefix}{curp_suffix}"
            curp_suffix += 1

            with self.assertRaises(ValidationError, msg=f"El correo {email} no debería ser válido."):
                member = self.create_member(curp = curp ,email=email)
                member.full_clean()

def test_invalid_phone_number(self):
    # Prueba con números de teléfono no válidos
    invalid_phone_numbers = [
        "12345a7890",       # Con una letra
        "1234567890a",      # Con una letra al final
        "123",              # Demasiado corto
        "1234567890123456", # Demasiado largo (exactamente 16 caracteres)
    ]
    curp_prefix = 'CARH010101HDFRRN'
    curp_suffix = 90

    for phone_number in invalid_phone_numbers:
        curp = f"{curp_prefix}{curp_suffix}"
        curp_suffix += 1

        if len(phone_number) > 15:
            # Para números más largos que 15 caracteres, espera un DataError
            with self.assertRaises(DataError):
                self.create_member(curp=curp, phone_number=phone_number)
        else:
            # Para formatos no válidos, espera un ValidationError
            with self.assertRaises(ValidationError):
                member = self.create_member(curp=curp, phone_number=phone_number)
                member.full_clean()  # Ejecuta las validaciones del modelo

        


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
