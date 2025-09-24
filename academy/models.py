from django.db import models
from django.utils.translation import gettext_lazy as _
from crm.models import AgeSegment, MedicalCondition, Member

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Código"))
    name = models.CharField(max_length=100, verbose_name=_("Nombre"))
    age_segments = models.ManyToManyField(AgeSegment, blank=True, verbose_name=_("Segmentos de edad"))
    medical_conditions = models.ManyToManyField(MedicalCondition, blank=True, verbose_name=_("Condiciones de salud"))
    members = models.ManyToManyField(Member, blank=True, verbose_name=_("Miembros"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name
