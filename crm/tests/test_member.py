import uuid
from datetime import date
from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.db import DataError
from crm.models import Member

class MemberTestCase(TestCase):
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

    def test_age_calculation(self):
        """Verifica que la edad calculada sea correcta."""
        birth_date = date.today().replace(year=date.today().year - 30)  # 30 años atrás
        member = self.create_member(birth_date=birth_date)
        self.assertEqual(member.age, 30, "La edad calculada no es la esperada.")