import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

class DiscoverySource(models.Model):
    """Model to represent discovery sources of the members (e.g., social media)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Source Name"))

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

class Member(models.Model):
    """Model representing a member of the academy or club with mandatory fields."""
    member_code = models.CharField(max_length=100, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False)
    curp = models.CharField(max_length=18, unique=True, blank=False)
    enrollment_date = models.DateField(auto_now_add=True, blank=True)
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
    how_did_you_hear = models.ForeignKey(DiscoverySource, on_delete=models.SET_NULL, null=True, blank=False, related_name='member_sources')
    how_did_you_hear_details = models.CharField(max_length=255, blank=True, null=True)
    
    # Health-related boolean fields
    has_illness = models.BooleanField(default=False, blank=False, verbose_name=_("Has any illness"))
    has_allergy = models.BooleanField(default=False, blank=False, verbose_name=_("Has any allergy"))
    has_flat_feet = models.BooleanField(default=False, blank=False, verbose_name=_("Has flat feet"))
    has_heart_conditions = models.BooleanField(default=False, blank=False, verbose_name=_("Has heart conditions"))

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

    def save(self, *args, user=None, **kwargs):
        # Save the member
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Call the base save method
        
        if is_new:
            # Only create the status log if it's a new member
            active_status = AccessStatus.objects.get(name=_("Active"))
            MemberAccessLog.objects.create(
                member=self,
                status=active_status,
                reason=_("New member"),
                changed_by=user,
            )


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

class MemberContact(models.Model):
    """Model to represent a contact for a member."""
    member = models.ForeignKey(Member, related_name='contacts', on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=15, blank=False)
    relation = models.CharField(max_length=100, blank=False)
    is_primary = models.BooleanField(default=False, blank=False)
    is_emergency = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return f"{self.name} ({self.relation})"
