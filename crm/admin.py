from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
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

# Inline model for Member contacts
class MemberContactInline(admin.TabularInline):
    model = MemberContact
    extra = 1
    classes = ('collapse',)
    fields = ('name', 'phone_number', 'relation', 'is_primary', 'is_emergency')

class MedicalConditionInline(admin.TabularInline):  # Puedes usar StackedInline si prefieres.
    model = Member.medical_conditions.through
    extra = 0  # Número de filas vacías adicionales
    can_delete = True

# Inline model for Member access logs
class MemberAccessLogInline(admin.TabularInline):
    model = MemberAccessLog
    extra = 0
    classes = ('collapse',)
    fields = ('status', 'reason', 'changed_by', 'date_changed')
    readonly_fields = ('changed_by', 'date_changed')  

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
        'photo_preview', 'member_code', 'last_name', 'second_last_name', 'name', 'phone_number', 'current_status'
    )
    search_fields = ('member_code', 'last_name', 'second_last_name','name', 'curp', 'email', 'phone_number')
    list_filter = ('gender',CurrentStatusFilter)
    ordering = ('member_code',)
    readonly_fields = ('member_code','enrollment_date', 'age', 'age_segment', 'photo_preview','current_status')
    # Add inlines for contacts and access logs
    inlines = [MemberContactInline, MemberAccessLogInline]
    def photo_preview(self, obj):
        """Method to display a photo preview in the admin."""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100" height="100" />')
        return _("No image available")

    photo_preview.short_description = _('Photo Preview')

    # Fieldsets for grouping fields in the admin form
    fieldsets = (
        (_('GENERAL INFORMATION'), {
            'fields': (
                'photo_preview','photo', 'member_code', 'last_name', 'second_last_name', 'name', 
                'current_status', 'curp', 'email', 'phone_number','gender', 'enrollment_date', 
                'birth_date', 'age', 'age_segment'
            ),
            'classes': ('collapse',)
        }),
        (_('HEALTH CONDITIONS'), {
            'fields': ('medical_conditions', 'medical_condition_details'),
            'classes': ('collapse',)
        }),
        (_('DISCOVERY SOURCE'), {
            'fields': ('how_did_you_hear', 'how_did_you_hear_details'),
            'classes': ('collapse',)
        }),
    )
