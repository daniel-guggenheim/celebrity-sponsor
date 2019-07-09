from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

# Create your views here.
from aiaUsers.models import BaseUserDetails
from campaignManager.forms import CampaignForm, CompanyPropositionForm
from campaignManager.models import Campaign, CompanyProposition


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def start_campaign(request):
    if request.method == 'POST':
        campaign_form = CampaignForm(request.POST)

        if campaign_form.is_valid():
            campaign_object = campaign_form.save(commit=False)
            campaign_object.company = request.user.user_details.company
            campaign_object.created_by = request.user
            campaign_object.last_modified_by = request.user
            now = timezone.now()
            campaign_object.creation_date = now
            campaign_object.last_update_date = now
            campaign_object.save()

            return HttpResponseRedirect(
                reverse('imageModifier:select_upload_campaign_logos', kwargs={'campaign_pk': campaign_object.pk}))
    else:
        campaign_form = CampaignForm()

    return render(request, 'campaign/start_campaign.html', {'campaign_form': campaign_form})


def modify_campaign(request, campaign_pk):
    campaign_to_modify = get_object_or_404(Campaign, pk=campaign_pk)

    if request.method == 'POST':
        campaign_form = CampaignForm(request.POST, instance=campaign_to_modify)

        if campaign_form.is_valid():
            campaign_object = campaign_form.save(commit=False)
            campaign_object.company = request.user.user_details.company
            campaign_object.created_by = request.user
            campaign_object.last_modified_by = request.user
            campaign_object.last_update_date = timezone.now()
            campaign_object.save()
            return HttpResponseRedirect(reverse('campaignManager:campaign_details', kwargs={'campaign_pk': campaign_object.pk}))
    else:
        campaign_form = CampaignForm(instance=campaign_to_modify)

    return render(request, 'campaign/start_campaign.html', {'campaign_form': campaign_form})


def campaign_list(request):
    my_company = request.user.user_details.company
    my_campaign_list = Campaign.objects.filter(company=my_company)
    return render(request, 'campaign/campaign_list.html', {'my_campaign_list': my_campaign_list})


def campaign_details(request, campaign_pk):
    my_campaign = get_object_or_404(Campaign, pk=campaign_pk)
    company_proposition_list = CompanyProposition.objects.filter(campaign=my_campaign)
    logos_list = my_campaign.company_logos.all()

    return render(request, 'campaign/campaign_details.html',
                  {'my_campaign': my_campaign, 'company_proposition_list': company_proposition_list, 'logos_list': logos_list})


def add_company_proposition(request, campaign_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    if request.method == 'POST':
        proposition_form = CompanyPropositionForm(request.POST)
        set_basic_worker_queryset(proposition_form)

        if proposition_form.is_valid():
            proposition = proposition_form.save(commit=False)
            proposition.campaign = campaign
            now = timezone.now()
            proposition.creation_date = now
            proposition.last_update_date = now
            proposition.last_modified_by = request.user
            proposition.save()
            proposition_form.save_m2m()
            if 'next_step' in request.POST:  # is the button to go to the next step is clicked
                return HttpResponseRedirect(
                    reverse('campaignManager:campaign_details', kwargs={'campaign_pk': campaign.pk}))
            else:
                return HttpResponseRedirect(
                    reverse('campaignManager:modify_company_proposition', kwargs={'proposition_pk': proposition.pk}))
    else:
        proposition_form = CompanyPropositionForm()
        set_basic_worker_queryset(proposition_form)

    return render(request, 'campaign/add_company_proposition.html', {'proposition_form': proposition_form})


def modify_company_proposition(request, proposition_pk):
    proposition_to_modify = get_object_or_404(CompanyProposition, pk=proposition_pk)
    if request.method == 'POST':
        proposition_form = CompanyPropositionForm(request.POST, instance=proposition_to_modify)
        set_worker_queryset(proposition_to_modify, proposition_form)

        if proposition_form.is_valid():
            proposition = proposition_form.save(commit=False)
            proposition.last_update_date = timezone.now()
            proposition.last_modified_by = request.user
            proposition.save()
            proposition_form.save_m2m()

            if 'next_step' in request.POST:  # is the button to go to the next step is clicked
                return HttpResponseRedirect(
                    reverse('campaignManager:campaign_details', kwargs={'campaign_pk': proposition.campaign.pk}))
            else:
                return HttpResponseRedirect(
                    reverse('campaignManager:modify_company_proposition', kwargs={'proposition_pk': proposition_pk}))
        print('proposition invalid')
    else:
        proposition_form = CompanyPropositionForm(instance=proposition_to_modify)
        set_worker_queryset(proposition_to_modify, proposition_form)

    return render(request, 'campaign/add_company_proposition.html',
                  {'proposition_form': proposition_form, 'proposition_pk': proposition_pk})


def set_worker_queryset(companyProposition, proposition_form):
    worker_set = get_user_model().objects.filter(user_details__user_type=BaseUserDetails.WORKER_VAL)
    try:
        avg_like = companyProposition.filter_average_nb_of_like_in_10_last_pictures
    except AttributeError:
        pass
    else:
        worker_set = worker_set.filter(user_details__average_nb_of_like_in_10_last_pictures_at_last_check__gte=avg_like)

    try:
        avg_followers = companyProposition.filter_nb_of_followers
    except AttributeError:
        print('exception avg_followers in company-proposition')
        pass
    else:
        worker_set = worker_set.filter(user_details__nb_of_followers_at_last_check__gte=avg_followers)

    try:
        successful_colab = companyProposition.filter_number_of_successful_past_collaborations
    except AttributeError:
        pass
    else:
        worker_set = worker_set.filter(user_details__number_of_successful_past_collaborations__gte=successful_colab)
    queryset_order_and_add_proposition(worker_set, proposition_form)


def set_basic_worker_queryset(proposition_form):
    worker_set = get_user_model().objects.filter(user_details__user_type=BaseUserDetails.WORKER_VAL)
    queryset_order_and_add_proposition(worker_set, proposition_form)


def queryset_order_and_add_proposition(worker_set, proposition_form):
    set_ordered = worker_set.order_by('user_details__nb_of_followers_at_last_check')
    proposition_form.fields['workers_selected'].queryset = set_ordered
