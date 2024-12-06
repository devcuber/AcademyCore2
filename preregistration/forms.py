import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Preregister
from crm.models import ContactRelation, MedicalCondition
from django.utils.translation import gettext_lazy as _

class PreRegisterAdminForm(forms.ModelForm):
    class Meta:
        model = Preregister
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Usa el selector de fecha nativo
            'medical_conditions': forms.CheckboxSelectMultiple(),  # Cambiar a checkboxes
        }

    def clean(self):
        cleaned_data = super().clean()
        medical_conditions = cleaned_data.get('medical_conditions')
        medical_condition_details = cleaned_data.get('medical_condition_details')

        # Validate that at least one medical condition is selected
        if not medical_conditions.exists():
            raise ValidationError("You must select at least one medical condition or choose 'None'.")

        # Validate the 'None' rule
        if medical_conditions.filter(name="None").exists() and medical_conditions.count() > 1:
            raise ValidationError("You cannot select other medical conditions if 'None' is selected.")

        # Validate the 'Other' rule
        if medical_conditions.filter(name="Other").exists() and not medical_condition_details:
            raise ValidationError("You must provide details of the medical condition if 'Other' is selected.")

        return cleaned_data
    
class PreRegisterPublicForm(forms.ModelForm):

    medical_conditions = forms.ModelMultipleChoiceField(
        queryset=MedicalCondition.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    # Campos adicionales para los contactos
    main_contact_name = forms.CharField(max_length=100)
    main_contact_phone = forms.CharField(max_length=20)
    main_contact_relation = forms.ModelChoiceField(queryset=ContactRelation.objects.all())
    
    emergency_contact_name = forms.CharField(max_length=100)
    emergency_contact_phone = forms.CharField(max_length=20)
    emergency_contact_relation = forms.ModelChoiceField(queryset=ContactRelation.objects.all())

    class Meta:
        model = Preregister
        fields = [
            'name', 'curp', 'birth_date', 'gender', 'phone_number', 'email',
            'photo', 'how_did_you_hear', 'how_did_you_hear_details', 'medical_condition_details'
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\d{10,15}$', phone_number):
            raise forms.ValidationError(
                _("The phone number must contain only digits and be between 10 and 15 characters long.")
            )
        return phone_number
    
    def clean_curp(self):
        curp = self.cleaned_data.get('curp')
        curp_pattern = r'^[A-Z]{4}\d{6}[HM]{1}[A-Z]{5}[A-Z0-9]{2}$'
        if not re.match(curp_pattern, curp):
            raise forms.ValidationError(
                _("The CURP must follow a valid format.")
            )
        return curp