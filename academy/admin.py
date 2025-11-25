from django.db import models
from django.forms import TimeInput
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from academy.models import Product, Instructor, AcademyProfile
from django import forms
from crm.models import Member
from crm.admin import MemberAdmin as BaseMemberAdmin

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'medical_conditions': forms.CheckboxSelectMultiple(),  # Cambiar a checkboxes
            'age_segments': forms.CheckboxSelectMultiple(),  # Cambiar a checkboxes
        }
    def clean(self):
        cleaned_data = super().clean()
        age_segments = cleaned_data.get('age_segments')
        medical_conditions = cleaned_data.get('medical_conditions')

        # Validar que al menos un segmento de edad esté seleccionado
        if not age_segments.exists():
            raise forms.ValidationError(_("You must select at least one age segment."))

        # Validar que al menos una condición médica esté seleccionada
        if not medical_conditions.exists():
            raise forms.ValidationError(_("You must select at least one medical condition."))

        return cleaned_data

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    exclude = ['members']
    form = ProductAdminForm

class AcademyProfileInline(admin.StackedInline):
    model = AcademyProfile
    extra = 0
    can_delete = False
    formfield_overrides = {
        models.TimeField: {"widget": TimeInput(format='%H:%M', attrs={"type": "time"})}
    }
admin.site.unregister(Member)

@admin.register(Member)
class MemberAdmin(BaseMemberAdmin):
    inlines = BaseMemberAdmin.inlines + [AcademyProfileInline]