from django.contrib import admin
from .models import Preregister
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe

@admin.register(Preregister)
class PreregisterAdmin(admin.ModelAdmin):
    list_display = (
        'photo_preview', 'folio','name'
    )
    search_fields = ( 'folio', 'name', 'curp', 'email')
    list_filter = ('gender',)
    ordering = ('folio',)
    readonly_fields = ('folio', 'age', 'age_segment', 'photo_preview')

    def photo_preview(self, obj):
        """Method to display a photo preview in the admin."""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100" height="100" />')
        return _("No image available")

    photo_preview.short_description = _('Photo Preview')

    # Fieldsets for grouping fields in the admin form
    fieldsets = (
        (_('General Information'), {
            'fields': (
                'photo_preview','photo', 'folio', 'name', 'curp', 'email', 'phone_number',
                'gender', 'birth_date', 'age', 'age_segment'
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