from django.test import TestCase
from academy.models import Product, AgeSegment, MedicalCondition
from academy.admin import ProductAdminForm

class ProductAdminFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear datos de prueba para AgeSegment y MedicalCondition
        cls.age_segment1 = AgeSegment.objects.get(name="Adult")
        cls.age_segment2 = AgeSegment.objects.get(name="Senior")
        cls.medical_condition1 = MedicalCondition.objects.create(name="Condition A")
        cls.medical_condition2 = MedicalCondition.objects.create(name="Condition B")

    def create_product_data(self, age_segments=None, medical_conditions=None):
        """Helper method to create form data for Product."""
        return {
            "code": "PROD001",
            "name": "Test Product",
            "age_segments": age_segments or [],
            "medical_conditions": medical_conditions or [],
        }

    def test_no_age_segments_selected(self):
        """Test that the form is invalid if no age segments are selected."""
        form_data = self.create_product_data(medical_conditions=[self.medical_condition1.id])
        form = ProductAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("You must select at least one age segment.", form.errors["__all__"])

    def test_no_medical_conditions_selected(self):
        """Test that the form is invalid if no medical conditions are selected."""
        form_data = self.create_product_data(age_segments=[self.age_segment1.id])
        form = ProductAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("You must select at least one medical condition.", form.errors["__all__"])

    def test_valid_form(self):
        """Test that the form is valid with both age segments and medical conditions selected."""
        form_data = self.create_product_data(
            age_segments=[self.age_segment1.id, self.age_segment2.id],
            medical_conditions=[self.medical_condition1.id, self.medical_condition2.id]
        )
        form = ProductAdminForm(data=form_data)
        self.assertTrue(form.is_valid())
