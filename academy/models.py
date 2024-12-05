from django.db import models
from crm.models import AgeSegment, MedicalCondition, Member


class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    age_segments = models.ManyToManyField(AgeSegment, blank=True)
    medical_conditions = models.ManyToManyField(MedicalCondition, blank=True)
    members = models.ManyToManyField(Member, blank=True)

    def __str__(self):
        return self.name