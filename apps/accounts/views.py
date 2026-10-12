from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView
from apps.accounts.forms import LoginForm
from apps.accounts.models import User, Role
from apps.accounts.permissions import AdminRequiredMixin

class CustomLoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
        return reverse('dashboard')


def custom_logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user_obj': request.user})


def access_denied_view(request, exception=None):
    return render(request, 'errors/403.html', {
        'message': str(exception) if exception else "You are not authorized to view this resource."
    }, status=403)


class UserManagementListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.select_related('department').all().order_by('-date_joined')
        role_filter = self.request.GET.get('role')
        if role_filter:
            qs = qs.filter(role=role_filter)
        search_query = self.request.GET.get('q')
        if search_query:
            qs = qs.filter(username__icontains=search_query) | qs.filter(first_name__icontains=search_query) | qs.filter(last_name__icontains=search_query)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = Role.choices
        ctx['selected_role'] = self.request.GET.get('role', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx
