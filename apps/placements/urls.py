from django.urls import path
from apps.placements import views

app_name = 'placements'

urlpatterns = [
    path('', views.placement_overview_view, name='overview'),
]
