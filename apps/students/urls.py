from django.urls import path
from apps.students import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('<str:student_id>/', views.student_detail_view, name='student_detail'),
]
