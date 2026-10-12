from django.urls import path
from apps.interventions import views

app_name = 'interventions'

urlpatterns = [
    path('', views.intervention_list_view, name='intervention_list'),
]
