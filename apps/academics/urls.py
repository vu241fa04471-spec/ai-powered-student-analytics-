from django.urls import path
from apps.academics import views

app_name = 'academics'

urlpatterns = [
    path('subjects/', views.subjects_list_view, name='subjects_list'),
]
