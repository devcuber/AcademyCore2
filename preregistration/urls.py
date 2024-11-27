from django.urls import path
from .views import PreregisterCreateView
from . import views

urlpatterns = [
    path('new/', PreregisterCreateView.as_view(), name='preregister_create'),
    path('success/', views.PreregisterSuccessView.as_view(), name='preregister_success'),
]
