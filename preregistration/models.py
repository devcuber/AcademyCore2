import uuid
from django.db import models
from crm.models import Person, Member, Contact
from django.utils.translation import gettext_lazy as _

class Preregister(Person):
    """Model representing a pre register member of the academy or club with mandatory fields."""
    folio = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    member = models.OneToOneField(Member, on_delete=models.SET_NULL, null=True, blank=False, related_name='preregister')
    medical_conditions = models.ManyToManyField('crm.MedicalCondition', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    accept_terms = models.BooleanField(default=False, verbose_name=_("Accepted Terms and Conditions"))
    
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('DONE', _('Done')),
        ('CANCELED', _('Canceled')),
    ]
    approval_status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='PENDING',verbose_name=_("approval status"))
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.folio:  # Generar solo si no existe
            self.folio = f"PR-{uuid.uuid4().hex[:8].upper()}"  # Ejemplo: PR-1A2B3C4D
        super().save(*args, **kwargs)

class PreRegisterContact(Contact):
    """Model to represent a contact for a member."""
    preregister = models.ForeignKey(Preregister, related_name='preregisters', on_delete=models.CASCADE, blank=False)

class TermsAndConditions(models.Model): 
    title = models.CharField(max_length=255, default='Términos y Condiciones') 
    pdf = models.FileField(upload_to='terms_and_conditions/') 
    
    def __str__(self): 
        return self.title