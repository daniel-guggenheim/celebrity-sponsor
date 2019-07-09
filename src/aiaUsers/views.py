from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView

from aiaUsers.models import BaseUserDetails, Company


@login_required
def account_profile(request):
    return render(request, 'profile.html')


def not_authorized(request):
    return render(request, 'aiaUsers/not_authorized.html')


def index(request):
    return render(request, 'index.html')


class TestUserCanAccessCompanyCreation(UserPassesTestMixin):
    """
    Handles the login authorization for company users.
    """
    def test_func(self):  # return true == the user can access the page
        try:
            # If it raises an exception then the user is not connected so it cannot access the page
            # If he is a company user and if he has not already a company, he can access the page.
            user_det = self.request.user.user_details
            return user_det.is_company_user_self() and not self.request.user.user_details.has_a_company()
        except AttributeError:
            # User not connected
            return False

    def get_login_url(self):
        """
        Return the good url for unauthorized user, depending of what he is.
        """
        user = self.request.user
        if not user.is_authenticated():
            return super(TestUserCanAccessCompanyCreation, self).get_login_url()
        elif not BaseUserDetails.is_company_user(user):
            return reverse('aiaUsers:not_authorized')
        elif user.user_details.has_a_company():
            return reverse('aiaUsers:company_details')
        else:
            raise AssertionError("This case has not been handled. The function get_login_url needs to be updated." +
                                 "The validation should be treated in test_func.")


class CompanyCreate(TestUserCanAccessCompanyCreation, CreateView):
    model = Company
    fields = ['name', 'abrev_name']
    success_url = reverse_lazy('aiaUsers:company_details')

    def form_valid(self, form):
        print('form valid')
        form.instance.created_by = self.request.user
        return super(CompanyCreate, self).form_valid(form)

    def get_success_url(self):
        self.request.user.user_details.company = self.object
        self.request.user.user_details.save()
        return super(CompanyCreate, self).get_success_url()


class CompanyUpdate(UpdateView):
    model = Company
    fields = ['name', 'abrev_name']
    success_url = reverse_lazy('aiaUsers:company_details')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('company_details')


@login_required
@user_passes_test(BaseUserDetails.is_company_user, login_url=reverse_lazy('aiaUsers:not_authorized'),
                  redirect_field_name='')
def company_details(request):
    user_det = request.user.user_details
    if not user_det.has_a_company():
        return redirect('aiaUsers:company_add')
    else:
        user_company = user_det.company.pk
        comp = get_object_or_404(Company, pk=user_company)
        return render(request, 'aiaUsers/company_detail.html', {'company': comp})
