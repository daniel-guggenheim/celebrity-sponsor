from django.conf.urls import url
from campaignManager import views

app_name = 'campaignManager'

urlpatterns = [
    url(r'^start/$', views.start_campaign, name='start_campaign'),
    url(r'^(?P<campaign_pk>\d+)/modify/$', views.modify_campaign, name='modify_campaign'),
    url(r'^(?P<campaign_pk>\d+)/add-proposition/$', views.add_company_proposition, name='add_company_proposition'),
    #url(r'^proposition/(?P<proposition_pk>[0-9]+)(?:/(?P<min_average_like>[0-9]+))?/$', views.modify_company_proposition, name='modify_company_proposition'),
    url(r'^proposition/(?P<proposition_pk>[0-9]+)/$', views.modify_company_proposition, name='modify_company_proposition'),
    url(r'^list/$', views.campaign_list, name='campaign_list'),
    url(r'^(?P<campaign_pk>\d+)/details/', views.campaign_details, name='campaign_details'),
]
