import uuid
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from crm.models import Member, MemberContact

def cancel_preregisters(modeladmin, request, queryset):
    """Cancela los PreRegister seleccionados."""
    canceled_count = 0

    with transaction.atomic():
        for preregister in queryset:
            if preregister.approval_status == "PENDING":
                preregister.approval_status = "CANCELED"
                preregister.save()
                canceled_count += 1

    if canceled_count > 0:
        modeladmin.message_user(request, f"{canceled_count} PreRegisters have been cancelled.")
    else:
        modeladmin.message_user(
            request, _("No registrations were canceled because they were already in DONE status."), level=messages.WARNING
        )

def convert_to_member(modeladmin, request, queryset):
    """Convierte los PreRegister seleccionados en Members."""
    converted_count = 0
    skipped_count = 0

    queryset = queryset.select_related('member').prefetch_related('medical_conditions', 'preregisters')

    for preregister in queryset:
        if not is_member_exists(preregister):
            try:
                with transaction.atomic():
                    new_member = create_member_from_preregister(preregister)
                    assign_medical_conditions(new_member, preregister)
                    create_member_contacts(new_member, preregister)
                    update_preregister_status(preregister, new_member)
                    cancel_duplicate_preregisters(preregister)

                    converted_count += 1

            except Exception as e:
                messages.error(request, f"Error al convertir {preregister.name}: {str(e)}")
        else:
            skipped_count += 1

    send_messages(modeladmin, request, converted_count, skipped_count)


def is_member_exists(preregister):
    """Verifica si ya existe un Member con el mismo CURP."""
    return Member.objects.filter(curp=preregister.curp).exists()


def create_member_from_preregister(preregister):
    """Crea un Member basado en los datos del Preregister."""
    return Member.objects.create(
        name=preregister.name,
        curp=preregister.curp,
        birth_date=preregister.birth_date,
        gender=preregister.gender,
        phone_number=preregister.phone_number,
        email=preregister.email,
        photo=preregister.photo,
        how_did_you_hear=preregister.how_did_you_hear,
        how_did_you_hear_details=preregister.how_did_you_hear_details,
        medical_condition_details=preregister.medical_condition_details,
        member_code=f"MEM-{uuid.uuid4().hex[:6].upper()}"
    )


def assign_medical_conditions(new_member, preregister):
    """Asigna las condiciones médicas al nuevo miembro."""
    new_member.medical_conditions.set(preregister.medical_conditions.all())


def create_member_contacts(new_member, preregister):
    """Crea los contactos del miembro desde el Preregister."""
    MemberContact.objects.bulk_create([
        MemberContact(
            member=new_member,
            name=contact.name,
            phone_number=contact.phone_number,
            relation=contact.relation,
            is_primary=contact.is_primary,
            is_emergency=contact.is_emergency,
        )
        for contact in preregister.preregisters.all()
    ])


def update_preregister_status(preregister, new_member):
    """Actualiza el Preregister, asignando el nuevo miembro y cambiando el status."""
    preregister.member = new_member
    preregister.approval_status = "DONE"
    preregister.save()


def cancel_duplicate_preregisters(preregister):
    """Cancela otros PreRegisters con el mismo CURP y status 'PENDING'."""
    preregister._meta.model.objects.filter(
        curp=preregister.curp,
        approval_status="PENDING"
    ).exclude(id=preregister.id).update(approval_status="CANCELED")


def send_messages(modeladmin, request, converted_count, skipped_count):
    """Envía los mensajes de éxito y advertencia al usuario."""
    if converted_count > 0:
        modeladmin.message_user(request, f"{converted_count} PreRegisters convertidos exitosamente a Members.")
    if skipped_count > 0:
        modeladmin.message_user(
            request,
            f"{skipped_count} PreRegisters omitidos debido a CURPs duplicados.",
            level=messages.WARNING
        )


convert_to_member.short_description = _("Convert selected items to Members")
