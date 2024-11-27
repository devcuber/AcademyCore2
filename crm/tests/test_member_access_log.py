import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from crm.models import Member, MemberAccessLog, AccessStatus

class MemberAccessLogTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Carga datos iniciales de prueba solo para los status, el usuario y la fuente de descubrimiento"""
        cls.user = User.objects.create_user(username="testuser", password="testpassword")

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
            "how_did_you_hear": None,
            "has_illness": False,
            "has_allergy": False,
            "has_flat_feet": False,
            "has_heart_conditions": False,
        }
        defaults.update(kwargs)
        return Member.objects.create(**defaults)

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
            how_did_you_hear=None
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
