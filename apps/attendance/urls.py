from django.urls import path
from apps.attendance import views

app_name = 'attendance'

urlpatterns = [
    path('shortages/', views.attendance_shortage_list_view, name='shortage_list'),
]
