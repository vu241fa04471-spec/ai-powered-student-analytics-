"""
URL configuration for smart_campus_analytics project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.accounts.dashboard_views import dashboard_view
from apps.students.api_views import StudentProfileViewSet, DepartmentViewSet, ProgramViewSet

# API Router
router = DefaultRouter()
router.register(r'students', StudentProfileViewSet, basename='api-students')
router.register(r'departments', DepartmentViewSet, basename='api-departments')
router.register(r'programs', ProgramViewSet, basename='api-programs')

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Main Dashboard
    path('', dashboard_view, name='dashboard'),

    # Modular App URLs
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('academics/', include('apps.academics.urls', namespace='academics')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('interventions/', include('apps.interventions.urls', namespace='interventions')),
    path('placements/', include('apps.placements.urls', namespace='placements')),

    # REST Framework API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Handler for 403 Forbidden
handler403 = 'apps.accounts.views.access_denied_view'
