from django.test import TestCase
from crm.models import MedicalCondition
from crm.admin import MemberAdminForm
from crm.models import DiscoverySource
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

def create_test_image():
    """Create a valid image file for testing."""
    image = Image.new('RGB', (100, 100), color='red')  # Crear una imagen roja de 100x100
    file = BytesIO()
    image.save(file, 'JPEG')  # Guardar la imagen en formato JPEG
    file.seek(0)  # Volver al inicio del archivo
    return SimpleUploadedFile("test_photo.jpg", file.read(), content_type="image/jpeg")

class MemberFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test data for medical conditions
        cls.none_condition = MedicalCondition.objects.get(name="None")
        cls.other_condition = MedicalCondition.objects.get(name="Other")
        cls.condition1 = MedicalCondition.objects.create(name="Condition 1")
        cls.condition2 = MedicalCondition.objects.create(name="Condition 2")
        cls.discovery_source = DiscoverySource.objects.create(name="Social Media")

    def create_member_data(self, medical_conditions, medical_condition_details=None):
        """Helper method to create form data."""
        return {
            "name":"name1",
            "birth_date": "1985-01-01",
            "member_code": "MEM001",
            "curp": "PEGA850101HDFRRL05",
            "gender": "M",
            "phone_number": "521234567890",
            "email": "juan.perez@example.com",
            "medical_conditions": medical_conditions,
            "medical_condition_details": medical_condition_details,
#           "photo": SimpleUploadedFile("test_photo.jpg", b"file_content", content_type="image/jpeg"),
            "how_did_you_hear": self.discovery_source,
        }

    def test_no_medical_conditions_selected(self):
        form_data = self.create_member_data(medical_conditions=[])
        form = MemberAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("You must select at least one medical condition or choose 'None'.", form.errors["__all__"])

    def test_none_with_other_conditions(self):
        form_data = self.create_member_data(
            medical_conditions=[self.none_condition.id, self.condition1.id]
        )
        form = MemberAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("You cannot select other medical conditions if 'None' is selected.", form.errors["__all__"])

    def test_other_without_details(self):
        form_data = self.create_member_data(
            medical_conditions=[self.other_condition.id]
        )
        form = MemberAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("You must provide details of the medical condition if 'Other' is selected.", form.errors["__all__"])

    def test_valid_none_selection(self):
        form_data = self.create_member_data(
            medical_conditions=[self.none_condition.id]
        )
        file = create_test_image()
        form = MemberAdminForm(data=form_data, files={'photo': file})
        print("Form errors:", form.errors)  # Muestra los errores si el formulario es inválido
        self.assertTrue(form.is_valid())

    def test_valid_other_with_details(self):
        form_data = self.create_member_data(
            medical_conditions=[self.other_condition.id],
            medical_condition_details="Details about the condition"
        )
        file = create_test_image()
        form = MemberAdminForm(data=form_data, files={'photo': file})
        self.assertTrue(form.is_valid())

    def test_valid_multiple_conditions(self):
        form_data = self.create_member_data(
            medical_conditions=[self.condition1.id, self.condition2.id]
        )
        file = create_test_image()
        form = MemberAdminForm(data=form_data, files={'photo': file})
        self.assertTrue(form.is_valid())

