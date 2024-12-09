from django.test import TestCase
from preregistration.forms import PreRegisterPublicForm
from crm.models import MedicalCondition, ContactRelation, DiscoverySource
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

class PreRegisterMedicalConditionTests(TestCase):
    def setUp(self):
        # Crear condiciones médicas de prueba
        self.none_condition = MedicalCondition.objects.get(name="None")
        self.asthma_condition = MedicalCondition.objects.create(name="Asthma")
        self.diabetes_condition = MedicalCondition.objects.create(name="Diabetes")

        # Crear DicoverySources
        self.social_media = DiscoverySource.objects.create(name="social_media")

        # Crear relaciones de contacto de prueba
        self.relation_parent = ContactRelation.objects.create(name="Parent")
        self.relation_sibling = ContactRelation.objects.create(name="Sibling")

        # Datos básicos del formulario
        self.form_data = {
            'name': 'Test User',
            'curp': 'TEST123456HDFABC01',
            'phone_number': '1234567890',
            'birth_date': '2000-01-01',
            'gender': 'M',
            'email': 'test@example.com',
            'main_contact_name': 'John Doe',
            'main_contact_phone': '0987654321',
            'main_contact_relation': self.relation_parent.id,
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '0123456789',
            'emergency_contact_relation': self.relation_sibling.id,
            'how_did_you_hear': self.social_media,
            'how_did_you_hear_details': 'Social Media',
            'accept_terms' : True,
        }

    def test_valid_form_single_medical_condition(self):
        """Test que el formulario es válido con una sola condición médica."""
        self.form_data['medical_conditions'] = [self.asthma_condition.id]
        file = create_test_image()
        form = PreRegisterPublicForm(data=self.form_data,files={'photo': file})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form_no_medical_conditions(self):
        """Test que el formulario no es válido sin condiciones médicas."""
        self.form_data['medical_conditions'] = []
        file = create_test_image()
        form = PreRegisterPublicForm(data=self.form_data,files={'photo': file})
        self.assertFalse(form.is_valid())
        self.assertIn('medical_conditions', form.errors)

    def test_invalid_form_none_with_other_conditions(self):
        """Test que el formulario no permite 'None' junto con otras condiciones."""
        self.form_data['medical_conditions'] = [self.none_condition.id, self.asthma_condition.id]
        file = create_test_image()
        form = PreRegisterPublicForm(data=self.form_data,files={'photo': file})
        self.assertFalse(form.is_valid())
        self.assertIn('medical_conditions', form.errors)

    def test_valid_form_multiple_conditions(self):
        """Test que el formulario es válido con múltiples condiciones médicas sin 'None'."""
        self.form_data['medical_conditions'] = [self.asthma_condition.id, self.diabetes_condition.id]
        file = create_test_image()
        form = PreRegisterPublicForm(data=self.form_data,files={'photo': file})
        self.assertTrue(form.is_valid(), form.errors)
