from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms
from .models import (
    Member, MemberContact, MemberAccessLog, DiscoverySource, AccessStatus,
    AgeSegment, MedicalCondition, ContactRelation
)

admin.site.register(AccessStatus)
admin.site.register(DiscoverySource)
admin.site.register(AgeSegment)
admin.site.register(MedicalCondition)
admin.site.register(ContactRelation)


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Usa el selector de fecha nativo
        }

# Inline model for Member contacts
class MemberContactInline(admin.TabularInline):
    model = MemberContact
    extra = 1
    fields = ('name', 'phone_number', 'relation', 'is_primary', 'is_emergency')

# Inline model for Member access logs
class MemberAccessLogInline(admin.TabularInline):
    model = MemberAccessLog
    extra = 0
    fields = ('status', 'reason', 'changed_by', 'date_changed')
    readonly_fields = ('status', 'reason', 'changed_by', 'date_changed')  # Todos los campos son de solo lectura

    def has_add_permission(self, request, obj=None):
        # No se permite agregar nuevos logs desde el inline
        return False

    def has_change_permission(self, request, obj=None):
        # No se permite editar los logs existentes
        return False

    def has_delete_permission(self, request, obj=None):
        # No se permite eliminar logs
        return False


class CurrentStatusFilter(SimpleListFilter):
    title = _('Current Status')  # Título del filtro
    parameter_name = 'current_status'  # Nombre del parámetro en la URL

    def lookups(self, request, model_admin):
        # Opciones que aparecerán en el filtro
        statuses = AccessStatus.objects.all()
        return [(status.id, status.name) for status in statuses]

    def queryset(self, request, queryset):
        # Filtra el queryset basado en la opción seleccionada
        if self.value():
            return queryset.filter(statuses__status_id=self.value()).distinct()
        return queryset

# Admin configuration for the Member model
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    form = MemberAdminForm
    list_display = (
        'photo_preview', 'member_code', 'name', 'current_status'
    )
    search_fields = ('member_code', 'name', 'curp', 'email')
    list_filter = ('gender',CurrentStatusFilter)
    ordering = ('member_code',)
    readonly_fields = ('enrollment_date', 'age', 'age_segment', 'photo_preview','current_status')

    # Add inlines for contacts and access logs
    inlines = [MemberContactInline, MemberAccessLogInline]

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
                'photo_preview','photo', 'member_code', 'name', 'current_status', 'curp', 'email', 'phone_number',
                'gender', 'enrollment_date', 'birth_date', 'age', 'age_segment'
            ),
        }),
        (_('Health Conditions'), {
            'fields': ('has_illness', 'has_allergy', 'has_flat_feet', 'has_heart_conditions', 'medical_condition', 'medical_condition_details'),
            'classes': ('collapse',)  # Collapse the 'Health Conditions' section
        }),
        (_('Discovery Source'), {
            'fields': ('how_did_you_hear', 'how_did_you_hear_details'),
            'classes': ('collapse',)  # Collapse the 'Discovery Source' section
        }),
    )
