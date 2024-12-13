import re
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

class DiscoverySource(models.Model):
    """Model to represent discovery sources of the members (e.g., social media)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Source Name"))

    def __str__(self):
        return self.name
    
class MedicalCondition(models.Model):
    """Model to represent discovery sources of the members (e.g., social media)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Condition Name"))

    def __str__(self):
        return self.name

class AccessStatus(models.Model):
    """Model to represent the status of a member (Active, Inactive, Temporarily Inactive)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Status Name"))

    class Meta:
        verbose_name = _("Access Status")
        verbose_name_plural = _("Access Statuses")

    def __str__(self):
        return self.name

class Person(models.Model):
    """Abstract model representing a person with common fields."""    
    name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    second_last_name = models.CharField(max_length=255, blank=False)
    curp = models.CharField(max_length=18, blank=False)
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
    how_did_you_hear = models.ForeignKey('crm.DiscoverySource', on_delete=models.SET_NULL, null=True, blank=False)
    how_did_you_hear_details = models.CharField(max_length=255, blank=True, null=True)  # Detalles de cómo se enteró de la academia
    medical_condition_details = models.CharField(max_length=255, blank=True, null=True)  # Detalles condiciones medicas

    # Métodos comunes
    @property
    def age(self):
        """Calcula la edad de la persona en base a birth_date."""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def age_segment(self):
        """Devuelve el segmento de edad correspondiente a la persona."""
        segment = AgeSegment.objects.filter(
            min_age__lte=self.age,  
            max_age__gt=self.age
        ).first()
        return segment

    def clean(self):
        """Validaciones para los campos comunes."""
        # Validación de número de teléfono (solo dígitos, entre 10 y 15 caracteres)
        if not re.match(r'^\d{10,15}$', self.phone_number):
            raise ValidationError(_("The phone number must contain only digits and be between 10 and 15 characters long."))

        # Validación de CURP (formato mexicano)
        curp_pattern = r'^[A-Z]{4}\d{6}[HM]{1}[A-Z]{5}[A-Z0-9]{2}$'
        if not re.match(curp_pattern, self.curp):
            raise ValidationError(_("The CURP must follow a valid format."))

        super().clean()  # Llamar al método clean() de la clase base para asegurarse de que no se omitan otras validaciones

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Member(Person):
    """Modelo que representa a un miembro de la academia o club, hereda de Person."""
    member_code = models.CharField(max_length=100, unique=True, blank=False)
    enrollment_date = models.DateField(auto_now_add=True, blank=True)  # Fecha de inscripción
    curp = models.CharField(max_length=18, unique=True, blank=False)  # Único solo en Member
    medical_conditions = models.ManyToManyField('crm.MedicalCondition', blank=True)

    def __str__(self):
        return f"({self.member_code}) {self.name}" 

    @property
    def current_status(self):
        """Devuelve el último estado del miembro según el log más reciente."""
        latest_log = self.statuses.order_by('-date_changed').first()
        return latest_log.status if latest_log else None

    def save(self, *args, user=None, **kwargs):
        """Método sobrecargado para guardar un miembro y crear un registro de acceso."""
        is_new = self.pk is None
        if is_new:
            self.member_code = self.generate_member_code()
        super().save(*args, **kwargs)
        
        if is_new:
            # Solo crear el registro de log si es un miembro nuevo
            active_status = AccessStatus.objects.get(name=_("Active"))
            MemberAccessLog.objects.create(
                member=self,
                status=active_status,
                reason=_("New member"),
                changed_by=user,
            )
    def generate_member_code(self):
        """Genera un nuevo member_code secuencial comenzando desde 5000."""
        MIN_CODE = 5000
        
        # Obtener todos los códigos actuales y ordenarlos
        existing_codes = Member.objects.values_list('member_code', flat=True)
        existing_codes = [int(code) for code in existing_codes if code.isdigit() and int(code) >= MIN_CODE]
        existing_codes.sort()
        
        # Buscar el primer hueco en la secuencia
        new_code = MIN_CODE
        for code in existing_codes:
            if new_code < code:
                break
            new_code += 1
        
        return str(new_code).zfill(4)

class MemberAccessLog(models.Model):
    """Model to represent the status log of a member."""
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='statuses', null=False, blank=False)
    status = models.ForeignKey(AccessStatus, on_delete=models.CASCADE, related_name='member_statuses', null=False, blank=False)
    reason = models.CharField(max_length=255, blank=False, null=False)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_changed = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def __str__(self):
        return f"{self.member.name} - {self.status.name} - {self.date_changed}"

    def save(self, *args, **kwargs):
        """Override save method to enforce non-modifiable status."""
        if self.pk is not None:  # If the instance already exists
            raise ValidationError(_("Cannot modify an existing status. You can only add new statuses."))
        
        super().save(*args, **kwargs)

class ContactRelation(models.Model):
    """Model to represent relations of the contacts to members"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Relation Name"))

    def __str__(self):
        return self.name

class Contact(models.Model):
    """Abstract model representing a contact with common fields."""    
    name = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=15, blank=False)
    relation = models.ForeignKey(ContactRelation, on_delete=models.SET_NULL, null=True, blank=True)
    is_primary = models.BooleanField(default=False, blank=False)
    is_emergency = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return f"{self.name} ({self.relation})"

    class Meta:
        abstract = True

class MemberContact(Contact):
    """Model to represent a contact for a member."""
    member = models.ForeignKey(Member, related_name='contacts', on_delete=models.CASCADE, blank=False)

class AgeSegment(models.Model):
    """Model to represent age segments (e.g., baby, child, adult, senior)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Segment Name"))
    min_age = models.PositiveIntegerField(verbose_name=_("Minimum Age"), help_text=_("Minimum age for this segment in years."))
    max_age = models.PositiveIntegerField(verbose_name=_("Maximum Age"), help_text=_("Maximum age for this segment in years."))

    class Meta:
        verbose_name = _("Age Segment")
        verbose_name_plural = _("Age Segments")
        ordering = ["min_age"]

    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age})"

    def clean(self):
        """Ensure that min_age is less than max_age and ranges do not overlap."""
        if self.min_age >= self.max_age:
            raise ValidationError(_("Minimum age must be less than maximum age."))

        # Check for overlapping ranges
        overlapping_segments = AgeSegment.objects.filter(
            min_age__lt=self.max_age,  # Inicio del segmento existente < fin del segmento actual
            max_age__gt=self.min_age   # Fin del segmento existente > inicio del segmento actual
        )
        if self.pk:  # Exclude the current instance when updating
            overlapping_segments = overlapping_segments.exclude(pk=self.pk)

        if overlapping_segments.exists():
            overlapping_segment_names = ", ".join([str(segment) for segment in overlapping_segments])
            raise ValidationError(
                _("The age range overlaps with an existing segment: %(segment)s."),
                params={"segment": overlapping_segment_names}
            )
        
        super().clean()
