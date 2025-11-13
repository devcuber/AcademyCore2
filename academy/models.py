from django.db import models
from django.utils.translation import gettext_lazy as _
from crm.models import AgeSegment, MedicalCondition, Member

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    age_segments = models.ManyToManyField(AgeSegment, blank=True, verbose_name=_("Age Segments"))
    medical_conditions = models.ManyToManyField(MedicalCondition, blank=True, verbose_name=_("Health Conditions"))
    members = models.ManyToManyField(Member, blank=True, verbose_name=_("Members"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name
