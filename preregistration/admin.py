from django.contrib import admin
from django.utils.html import format_html 
from django.urls import reverse
from crm.models import Member
from .models import Preregister,PreRegisterContact, TermsAndConditions
from .actions import convert_to_member, cancel_preregisters
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Case, When, IntegerField
from .forms import PreRegisterAdminForm
from crm.admin import MemberAdmin

class PreregisterContactInline(admin.TabularInline):
    model = PreRegisterContact
    extra = 1
    fields = ('name', 'phone_number', 'relation', 'is_primary', 'is_emergency')

class PreregisterLinkInline(admin.TabularInline):
    model = Preregister
    extra = 0
    can_delete = False
    fields = ["view_preregister"]
    readonly_fields = ["view_preregister"]

    # Evitar mostrar formulario
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def view_preregister(self, obj):
        if not obj:
            return "No hay preregistro asociado"

        url = reverse("admin:preregistration_preregister_change", args=[obj.id])
        fecha = obj.created_at.strftime("%Y-%m-%d %H:%M")

        return format_html(
            '<a href="{}">Ver preregistro: {} Creado: {} </a>',
            url,
            obj.folio,
            fecha
        )
    view_preregister.short_description = "Preregister"

@admin.register(Preregister)
class PreregisterAdmin(admin.ModelAdmin):
    form = PreRegisterAdminForm
    actions = [convert_to_member, cancel_preregisters]  # Agrega la acción personalizada
    list_display = (
        'photo_preview', 'folio', 'last_name', 'second_last_name', 'name', 'phone_number', 'approval_status'
    )
    search_fields = ( 'folio', 'last_name', 'second_last_name', 'name', 'curp', 'email', 'phone_number')
    list_filter = ('approval_status',)
    ordering = ('folio',)
    readonly_fields = ('folio', 'age', 'age_segment', 'photo_preview', 'approval_status', 'created_at')
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
                'approval_status','photo_preview','photo', 'folio', 'last_name', 'second_last_name', 'name', 'curp', 'email', 'address', 'phone_number',
                'gender', 'birth_date', 'age', 'age_segment'
            ),
        }),
        (_('HEALTH CONDITIONS'), {
            'fields': ('medical_conditions', 'medical_condition_details','height','weight','blood_type'),
            'classes': ('collapse',)
        }),
        (_('DISCOVERY SOURCE'), {
            'fields': ('how_did_you_hear', 'how_did_you_hear_details'),
            'classes': ('collapse',)
        }),
        (_('TERMS AND CONDITIONS'), {
            'fields': ('accept_terms', 'created_at'),
            'classes': ('collapse',)
        }),
    )

class TermsAndConditionsAdmin(admin.ModelAdmin): 
    list_display = ['title'] 
    fields = ['pdf'] 
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)

