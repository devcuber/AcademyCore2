from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from academy.models import Product
from django import forms
from crm.models import Member
from crm.admin import MemberAdmin, MemberAdminForm as BaseMemberAdminForm 

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

class ProductInline(admin.TabularInline):  # TabularInline muestra la relación en forma de tabla
    model = Member.product_set.through  # Tabla intermedia de la relación M2M
    extra = 1  # Número de filas vacías para agregar nuevos productos
    verbose_name = _("Product")  # Singular
    verbose_name_plural = _("Products")  # Plural
    classes = ('collapse',)

#class CustomMemberAdmin(MemberAdmin):
#    #ProductInline en la penultima posición, respetando los access_logs en la última posición
#    inlines = MemberAdmin.inlines[:-1] + [ProductInline] + MemberAdmin.inlines[-1:]
#    class Media:
#        js = ('js/filter_products.js',)
#
#admin.site.unregister(Member)
#admin.site.register(Member, CustomMemberAdmin)