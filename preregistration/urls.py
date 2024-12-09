from django.urls import path
from .views import PreregisterCreateView, PreregisterSuccessView, TermsAndConditionsView

urlpatterns = [
    path('new/', PreregisterCreateView.as_view(), name='preregister_create'),
    path('success/', PreregisterSuccessView.as_view(), name='preregister_success'),
    path('terms-and-conditions/', TermsAndConditionsView.as_view(), name='terms_and_conditions'),
]
