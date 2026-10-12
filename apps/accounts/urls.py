from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.UserManagementListView.as_view(), name='user_list'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
]
