from django.contrib import admin
from .models import Preregister,PreRegisterContact
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe

class PreregisterContactInline(admin.TabularInline):
    model = PreRegisterContact
    extra = 1
    fields = ('name', 'phone_number', 'relation', 'is_primary', 'is_emergency')

@admin.register(Preregister)
class PreregisterAdmin(admin.ModelAdmin):
    list_display = (
        'photo_preview', 'folio','name','approval_status'
    )
    search_fields = ( 'folio', 'name', 'curp', 'email')
    list_filter = ('gender','approval_status')
    ordering = ('folio',)
    readonly_fields = ('folio', 'age', 'age_segment', 'photo_preview', 'approval_status')
    inlines = [PreregisterContactInline]

    def get_queryset(self, request):
        """
        Modifica el queryset por defecto para mostrar solo los preregistros con estado 'Pending'.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(approval_status='PENDING')  # Filtra por estado Pending

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
                'approval_status','photo_preview','photo', 'folio', 'name', 'curp', 'email', 'phone_number',
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