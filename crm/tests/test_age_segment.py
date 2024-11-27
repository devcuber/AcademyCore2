import uuid
from unittest import skip
from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from crm.models import Member, AgeSegment
from django.test import TestCase

class MemberAgeSegmentTestCase(TestCase):

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

    def test_correct_age_segment_assignment(self):
        """Verifica que se asigne el segmento de edad correcto según la fecha de nacimiento."""
        test_cases = [
            {"birth_date": date.today().replace(year=date.today().year - 1), "expected_segment": AgeSegment.objects.get(name=("Baby"))},
            {"birth_date": date.today().replace(year=date.today().year - 10), "expected_segment": AgeSegment.objects.get(name=("Child"))},
            {"birth_date": date.today().replace(year=date.today().year - 30), "expected_segment": AgeSegment.objects.get(name=("Adult"))},
            {"birth_date": date.today().replace(year=date.today().year - 70), "expected_segment": AgeSegment.objects.get(name=("Senior"))},
        ]

        curp_prefix  = 'ABCH010101HDFRRN'
        curp_suffix = 10

        for case in test_cases:
            curp = f"{curp_prefix}{curp_suffix}"
            curp_suffix += 1
            with self.subTest(birth_date=case["birth_date"], expected_segment=case["expected_segment"]):
                member = self.create_member(curp=curp, birth_date=case["birth_date"])
                self.assertEqual(
                    member.age_segment, 
                    case["expected_segment"], 
                    f"El segmento asignado no coincide para la fecha de nacimiento {case['birth_date']}."
                )
    def test_min_age_less_than_max_age(self):
        """Verifica que no se permita un segmento con min_age >= max_age."""
        invalid_segment = AgeSegment(name="Invalid", min_age=15, max_age=10)
        with self.assertRaises(ValidationError, msg="Debería lanzarse un ValidationError para min_age >= max_age."):
            invalid_segment.full_clean()

    def test_no_overlapping_segments(self):
        """Verifica que no se puedan agregar segmentos que traslapen."""
        overlapping_segment = AgeSegment(name="Overlap", min_age=10, max_age=15)
        with self.assertRaises(ValidationError, msg="No se deberían permitir segmentos traslapados."):
            overlapping_segment.full_clean()
    
    def test_can_modify_and_add_non_overlapping_segments(self):
        """Verifica que se pueda modificar un segmento existente y agregar otro que no traslape."""
        # Modificar el segmento existente
        child_segment = AgeSegment.objects.get(name=("Child"))
        child_segment.min_age = 2
        child_segment.max_age = 13
        child_segment.full_clean()
        child_segment.save()

        # Crear un nuevo segmento no traslapado
        teen_segment = AgeSegment(name="Teen", min_age=13, max_age=18)
        teen_segment.full_clean()
        teen_segment.save()

        # Validar resultados
        self.assertTrue(AgeSegment.objects.filter(name="Child").exists(), "El segmento 'Child' debería existir.")
        self.assertTrue(AgeSegment.objects.filter(name="Teen").exists(), "El segmento 'Teen' debería existir.")
