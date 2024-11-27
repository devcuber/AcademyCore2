import uuid
from django.db import models
from crm.models import Person, Member, DiscoverySource  
from django.utils.translation import gettext_lazy as _


class Preregister(Person):
    """Model representing a pre register member of the academy or club with mandatory fields."""
    folio = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=False, related_name='member')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.folio:  # Generar solo si no existe
            self.folio = f"PR-{uuid.uuid4().hex[:8].upper()}"  # Ejemplo: PR-1A2B3C4D
        super().save(*args, **kwargs)