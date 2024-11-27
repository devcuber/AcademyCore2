from django.shortcuts import render

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .models import Preregister
from django.http import HttpResponseRedirect

class PreregisterCreateView(CreateView):
    model = Preregister
    fields = [
        'name', 'curp', 'birth_date', 'gender', 'phone_number', 'email', 
        'photo', 'how_did_you_hear', 'how_did_you_hear_details', 
        'has_illness', 'has_allergy', 'has_flat_feet', 'has_heart_conditions'
    ]
    template_name = 'preregistration/preregister_form.html'  # El nombre de la plantilla HTML
    success_url = reverse_lazy('preregister_success')  # Redirige tras guardar

    def form_invalid(self, form):
        print("Formulario no válido:", form.errors)  # Depuración en consola
        return super().form_invalid(form)
    
    def form_valid(self, form):
        self.object = form.save()  # Guarda el objeto y lo asigna a `self.object`
        return HttpResponseRedirect(self.get_success_url() + f"?folio={self.object.folio}")

class PreregisterSuccessView(TemplateView):
    template_name = 'preregistration/preregister_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folio'] = self.request.GET.get('folio')  # Extrae el folio de la URL
        return context
