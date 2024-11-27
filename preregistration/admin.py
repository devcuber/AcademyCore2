from django.contrib import admin
from .models import Preregister
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe

@admin.register(Preregister)
class PreregisterAdmin(admin.ModelAdmin):
    list_display = (
        'folio','photo_preview', 'name'
    )
    search_fields = ( 'folio', 'name', 'curp', 'email')
    list_filter = ('gender',)
    ordering = ('folio',)
    readonly_fields = ('calculate_age', 'photo_preview')

    def calculate_age(self, obj):
        """Method to calculate the member's age based on their birth date."""
        if obj.birth_date:
            today = timezone.now().date()
            age = today.year - obj.birth_date.year
            if today.month < obj.birth_date.month or (
                today.month == obj.birth_date.month and today.day < obj.birth_date.day
            ):
                age -= 1
            return age
        return _("Not available")

    calculate_age.short_description = _('Age')

    def photo_preview(self, obj):
        """Method to display a photo preview in the admin."""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100" height="100" />')
        return _("No image available")

    photo_preview.short_description = _('Photo Preview')

    #def save_model(self, request, obj, form, change):
    #    # Guarda el objeto Member primero para asignar un ID
    #    super().save_model(request, obj, form, change)
#
    #    # Realiza validaciones relacionadas después de guardar
    #    primary_contacts = obj.contacts.filter(is_primary=True)
    #    emergency_contacts = obj.contacts.filter(is_emergency=True)
#
    #    if primary_contacts.count() != 1:
    #        raise ValueError(_("There must be exactly one primary contact."))
    #    if emergency_contacts.count() != 1:
    #        raise ValueError(_("There must be exactly one emergency contact."))

    # Fieldsets for grouping fields in the admin form
    fieldsets = (
        (_('General Information'), {
            'fields': (
                'photo_preview','photo', 'member', 'name', 'curp', 'email', 'phone_number',
                'gender', 'birth_date', 'calculate_age'
            ),
        }),
        (_('Health Conditions'), {
            'fields': ('has_illness', 'has_allergy', 'has_flat_feet', 'has_heart_conditions'),
            'classes': ('collapse',)  # Collapse the 'Health Conditions' section
        }),
        (_('Discovery Source'), {
            'fields': ('how_did_you_hear', 'how_did_you_hear_details'),
            'classes': ('collapse',)  # Collapse the 'Discovery Source' section
        }),
    )