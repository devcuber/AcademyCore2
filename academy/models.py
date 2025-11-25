from django.db import models
from django.utils.translation import gettext_lazy as _
from crm.models import AgeSegment, MedicalCondition, Member

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    age_segments = models.ManyToManyField(AgeSegment, blank=True, verbose_name=_("Age Segments"))
    medical_conditions = models.ManyToManyField(MedicalCondition, blank=True, verbose_name=_("Health Conditions"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

class Instructor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class AcademyProfile(models.Model):
    member = models.OneToOneField(Member,on_delete=models.CASCADE,related_name="academy_profile")
    instructor = models.ForeignKey(Instructor,on_delete=models.SET_NULL,null=True,blank=True,related_name="members")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True,related_name="members")
    start_time = models.TimeField(null=True, blank=True, verbose_name=_("Hora inicio"))
    end_time = models.TimeField(null=True, blank=True, verbose_name=_("Hora fin"))

    def __str__(self):
        return f"Academy profile for {self.member.member_code}"