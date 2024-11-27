import re
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from crm.models import DiscoverySource, Member
from django.utils.translation import gettext_lazy as _


class Preregister(models.Model):
    """Model representing a pre register member of the academy or club with mandatory fields."""
    folio = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=255, blank=False)
    curp = models.CharField(max_length=18, unique=True, blank=False)
    birth_date = models.DateField(blank=False)
    
    gender_choices = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=False)
    phone_number = models.CharField(max_length=15, blank=False)
    email = models.EmailField(blank=False)
    photo = models.ImageField(upload_to='members_photos/', blank=False)
    how_did_you_hear = models.ForeignKey(DiscoverySource, on_delete=models.SET_NULL, null=True, blank=False, related_name='preregisters')
    how_did_you_hear_details = models.CharField(max_length=255, blank=True, null=True)
    
    # Health-related boolean fields
    has_illness = models.BooleanField(default=False, blank=False, verbose_name=_("Has any illness"))
    has_allergy = models.BooleanField(default=False, blank=False, verbose_name=_("Has any allergy"))
    has_flat_feet = models.BooleanField(default=False, blank=False, verbose_name=_("Has flat feet"))
    has_heart_conditions = models.BooleanField(default=False, blank=False, verbose_name=_("Has heart conditions"))

    #
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=False, related_name='member')

    def __str__(self):
        return self.name

    def clean(self):
        # Phone number validation (only digits, between 10 and 15 characters)
        if not re.match(r'^\d{10,15}$', self.phone_number):
            raise ValidationError(_("The phone number must contain only digits and be between 10 and 15 characters long."))

        # CURP validation (Mexican CURP format)
        curp_pattern = r'^[A-Z]{4}\d{6}[HM]{1}[A-Z]{5}[A-Z0-9]{2}$'
        if not re.match(curp_pattern, self.curp):
            raise ValidationError(_("The CURP must follow a valid format."))

        # Call the parent's clean() method to ensure no other field validations are missed
        super().clean()

    def save(self, *args, **kwargs):
        if not self.folio:  # Generar solo si no existe
            self.folio = f"PR-{uuid.uuid4().hex[:8].upper()}"  # Ejemplo: PR-1A2B3C4D
        super().save(*args, **kwargs)