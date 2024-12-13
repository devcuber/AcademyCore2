from django.contrib import admin
from django.utils.html import format_html 
from django.urls import reverse
from crm.models import Member
from .models import Preregister,PreRegisterContact
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
                'approval_status','photo_preview','photo', 'folio', 'last_name', 'second_last_name', 'name', 'curp', 'email', 'phone_number',
                'gender', 'birth_date', 'age', 'age_segment'
            ),
        }),
        (_('HEALTH CONDITIONS'), {
            'fields': ('medical_conditions', 'medical_condition_details'),
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

class CustomMemberAdmin(MemberAdmin):
    def get_preregister_info(self, obj): 
        if hasattr(obj, 'preregister') and obj.preregister: 
            preregister_url = reverse('admin:preregistration_preregister_change', args=[obj.preregister.id]) 
            return format_html('<a href="{}">Folio: {}, Creado: {}</a>', preregister_url, obj.preregister.folio, obj.preregister.created_at) 
        return "No tiene preregistro asociado."

    get_preregister_info.short_description = _("PreRegister Information")
    fieldsets = tuple(list(MemberAdmin.fieldsets) + [
        (_('PREREGISTER INFORMATION'), {
            'fields': ('get_preregister_info',),
            'classes': ('collapse',)
        })
    ])
    readonly_fields = tuple(list(MemberAdmin.readonly_fields) + ['get_preregister_info'] )

admin.site.unregister(Member)
admin.site.register(Member, CustomMemberAdmin)