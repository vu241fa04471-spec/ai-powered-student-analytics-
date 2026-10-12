from django.urls import path
from apps.analytics import views

app_name = 'analytics'

urlpatterns = [
    path('risks/', views.risk_dashboard_view, name='risk_dashboard'),
    path('segments/', views.segments_view, name='segments'),
]
