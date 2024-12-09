from django.contrib import admin
from .models import Preregister,PreRegisterContact
from .actions import convert_to_member, cancel_preregisters
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Case, When, IntegerField
from .forms import PreRegisterAdminForm

class PreregisterContactInline(admin.TabularInline):
    model = PreRegisterContact
    extra = 1
    fields = ('name', 'phone_number', 'relation', 'is_primary', 'is_emergency')

@admin.register(Preregister)
class PreregisterAdmin(admin.ModelAdmin):
    form = PreRegisterAdminForm
    actions = [convert_to_member, cancel_preregisters]  # Agrega la acción personalizada
    list_display = (
        'photo_preview', 'folio','name','approval_status'
    )
    search_fields = ( 'folio', 'name', 'curp', 'email')
    list_filter = ('approval_status',)
    ordering = ('folio',)
    readonly_fields = ('folio', 'age', 'age_segment', 'photo_preview', 'approval_status')
    inlines = [PreregisterContactInline]

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
        (_('HEALTH CONDITIONS'), {
            'fields': ('medical_conditions', 'medical_condition_details'),
            'classes': ('collapse',)
        }),
        (_('Discovery Source'), {
            'fields': ('how_did_you_hear', 'how_did_you_hear_details'),
            'classes': ('collapse',)  # Collapse the 'Discovery Source' section
        }),
    )