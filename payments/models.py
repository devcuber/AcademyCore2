# payments/models.py

from django.db import models
from crm.models import Member
from django.utils.translation import gettext_lazy as _

class MemberPaymentProfile(models.Model):
    DUE_DAY_CHOICES = [
        (15, "Día 15"),
        (30, "Día 30"),
    ]

    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name="payment_profile"
    )

    due_day = models.IntegerField(choices=DUE_DAY_CHOICES, verbose_name=_("Due Day"))
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("monthly fee"))

    class Meta:
        verbose_name = _("Member Payment Profile")
        verbose_name_plural = _("Member Payment Profiles")

    def __str__(self):
        return f"Perfil de pago de {self.member.member_code}"
