from django.urls import path, include
from .views import PreregisterCreateView, PreregisterSuccessView, TermsAndConditionsView

urlpatterns = [
    path('new/', PreregisterCreateView.as_view(), name='preregister_create'),
    path('success/', PreregisterSuccessView.as_view(), name='preregister_success'),
    path('terms-and-conditions/', TermsAndConditionsView.as_view(), name='terms_and_conditions'),
    path('i18n/', include('django.conf.urls.i18n')),  # permite cambiar idioma vía POST
]
