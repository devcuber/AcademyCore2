# payments/admin.py

from django.contrib import admin
from crm.models import Member
from payments.models import MemberPaymentProfile

from crm.admin import MemberAdmin as BaseMemberAdmin
from academy.admin import AcademyProfileInline

class MemberPaymentProfileInline(admin.StackedInline):
    model = MemberPaymentProfile
    extra = 0
    can_delete = False

admin.site.unregister(Member)

@admin.register(Member)
class MemberAdmin(BaseMemberAdmin):
    inlines = BaseMemberAdmin.inlines + [AcademyProfileInline, MemberPaymentProfileInline]
