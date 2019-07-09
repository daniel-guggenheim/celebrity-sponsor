from django.conf.urls import url

from . import views

app_name = 'aiaUsers'

urlpatterns = [
    url(r'^profile/$', views.account_profile, name='account_profile'),
    url(r'^forbidden/$', views.not_authorized, name='not_authorized'),
    url(r'^company/add/$', views.CompanyCreate.as_view(), name='company_add'),
    url(r'^company/(?P<pk>[0-9]+)/$', views.CompanyUpdate.as_view(), name='company_update'),
    url(r'^company/(?P<pk>[0-9]+)/delete/$', views.CompanyDelete.as_view(), name='company_delete'),
    url(r'^company/details/$', views.company_details, name='company_details'),
]
