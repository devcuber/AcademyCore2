from django.shortcuts import render

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .models import Preregister, PreRegisterContact
from crm.models import MedicalCondition, ContactRelation
from django.http import HttpResponseRedirect
from .forms import PreRegisterPublicForm

class PreregisterCreateView(CreateView):
    model = Preregister
    form_class = PreRegisterPublicForm
    #fields = [
    #    'name', 'curp', 'birth_date', 'gender', 'phone_number', 'email', 
    #    'photo', 'how_did_you_hear', 'how_did_you_hear_details'
    #]
    template_name = 'preregistration/preregister_form.html'  # El nombre de la plantilla HTML
    success_url = reverse_lazy('preregister_success')  # Redirige tras guardar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medical_conditions'] = MedicalCondition.objects.all()
        context['contact_relations'] = ContactRelation.objects.all()
        return context

    def form_invalid(self, form):
        print("Formulario no válido:", form.errors)  # Depuración en consola
        return super().form_invalid(form)
    
    def form_valid(self, form):
        # Guarda la preinscripción
        self.object = form.save()

        medical_conditions = form.cleaned_data['medical_conditions']
        for condition in medical_conditions:
            self.object.medical_conditions.add(condition)

        # Captura los datos de los contactos
        main_contact_name = form.cleaned_data['main_contact_name']
        main_contact_phone = form.cleaned_data['main_contact_phone']
        main_contact_relation = form.cleaned_data['main_contact_relation']
        
        emergency_contact_name = form.cleaned_data['emergency_contact_name']
        emergency_contact_phone = form.cleaned_data['emergency_contact_phone']
        emergency_contact_relation = form.cleaned_data['emergency_contact_relation']

        # Crear el contacto principal
        PreRegisterContact.objects.create(
            preregister=self.object,
            name=main_contact_name,
            phone_number=main_contact_phone,
            relation=main_contact_relation,
            is_primary=True
        )

        # Crear el contacto de emergencia
        PreRegisterContact.objects.create(
            preregister=self.object,
            name=emergency_contact_name,
            phone_number=emergency_contact_phone,
            relation=emergency_contact_relation,
            is_emergency=True
        )

        return HttpResponseRedirect(self.get_success_url() + f"?folio={self.object.folio}")

class PreregisterSuccessView(TemplateView):
    template_name = 'preregistration/preregister_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folio'] = self.request.GET.get('folio')  # Extrae el folio de la URL
        return context
