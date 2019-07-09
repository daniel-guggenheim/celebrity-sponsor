from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from aiaUsers.models import BaseUserDetails, CompanyUserDetails
from campaignManager.models import Campaign, Auction, AuctionElement, UserProposition
from imageModifier.forms import UploadImageForm, SelectUploadCampaignLogosForm, SelectAuctionElementForm, \
    ImageProcessingParametersForm
from imageModifier.models import CompanyLogoImage, TransformedImageBuilder


def index(request):
    return HttpResponseRedirect(reverse('imageModifier:uploadCompanyImage'))


@login_required
@user_passes_test(BaseUserDetails.is_company_user, login_url=reverse_lazy('aiaUsers:not_authorized'),
                  redirect_field_name='')
@user_passes_test(CompanyUserDetails.global_has_a_company, login_url=reverse_lazy('aiaUsers:company_add'))
def select_upload_campaign_logos(request, campaign_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    user_company = request.user.user_details.company
    flag_logo_representative_erased = False

    if request.method == 'POST':
        form = SelectUploadCampaignLogosForm(user_company, campaign, request.POST, request.FILES)  # get the form
        if form.is_valid():
            logo_representative = form.cleaned_data['logo_representative']
            # We try to get the image. If no image was uploaded, then MultiValueDictKeyError exception is thrown and the step
            # is skipped (no image is saved)
            try:
                image_uploaded = request.FILES['uploaded_image']
                new_image = CompanyLogoImage(related_company=user_company, uploaded_by=request.user, pub_date=timezone.now(),
                                             companyImageUploaded=image_uploaded)
                new_image.save()
                campaign.company_logos.add(new_image)
            except MultiValueDictKeyError:
                pass
            # Make the change with the 2 forms.
            for logo in form.cleaned_data['logos_to_select']:
                campaign.company_logos.add(logo)
            for logo in form.cleaned_data['logos_to_deselect']:
                campaign.company_logos.remove(logo)
                if logo == logo_representative:  # the logo representative is being erased from the list.
                    campaign.company_logo_representative = None
                    flag_logo_representative_erased = True

            # If the logo representative currently selected is being erased or is None -> Attribute a default
            # from the list (or None if the list is empty)
            if flag_logo_representative_erased or logo_representative is None:
                campaign.company_logo_representative = campaign.company_logos.first()
            else:  # Normally saving logo representative
                campaign.company_logo_representative = logo_representative

            campaign.save()

            if 'next_step' in request.POST:  # is the button to go to the next step is clicked
                return HttpResponseRedirect(
                    reverse('campaignManager:add_company_proposition', kwargs={'campaign_pk': campaign_pk}))
            else:
                return HttpResponseRedirect(
                    reverse('imageModifier:select_upload_campaign_logos', kwargs={'campaign_pk': campaign_pk}))

    else:
        form = SelectUploadCampaignLogosForm(user_company, campaign)

    # Load the list of company logos
    company_logo_list = CompanyLogoImage.objects.filter(related_company=user_company)

    # Render list page with the company logos and the form
    return render(request,
                  'imageModifier/select_upload_campaign_logos.html', {
                      'companyLogoList': company_logo_list,
                      'form': form},
                  )


@login_required
@user_passes_test(BaseUserDetails.is_company_user, login_url=reverse_lazy('aiaUsers:not_authorized'),
                  redirect_field_name='')
@user_passes_test(CompanyUserDetails.global_has_a_company, login_url=reverse_lazy('aiaUsers:company_add'))
def upload_company_image(request):
    user_company = request.user.user_details.company
    # File upload
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            newimage = CompanyLogoImage(related_company=user_company, uploaded_by=request.user, pub_date=timezone.now(),
                                        companyImageUploaded=request.FILES['uploaded_image'])
            newimage.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('imageModifier:uploadCompanyImage'))
    else:
        form = UploadImageForm()  # A empty, unbound form

    # Load the list of company logos
    companyLogoList = CompanyLogoImage.objects.filter(related_company=user_company)

    # Render list page with the company logos and the form
    return render(request,
                  'imageModifier/uploadCompanyImage.html', {
                      'companyLogoList': companyLogoList,
                      'form': form},
                  )


def upload_transformable_image(request, user_proposition_pk):
    user_prop = get_object_or_404(UserProposition, pk=user_proposition_pk)
    old_image_transf_builder = None
    try:
        old_image_transf_builder = user_prop.transformedimagebuilder
    except AttributeError:
        pass

    # File upload
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            if old_image_transf_builder:
                old_image_transf_builder.delete()
            now = timezone.now()
            transformed_image_builder = TransformedImageBuilder(upload_date=now, last_update_date=now,
                                                                user_proposition=user_prop,
                                                                base_image=request.FILES['uploaded_image'])
            transformed_image_builder.save()
            # Redirect to the document list after POST
            return HttpResponseRedirect(
                reverse('imageModifier:image_processing', kwargs={'user_proposition_pk': user_proposition_pk}))
    else:
        form = UploadImageForm()

    # Render list page with the documents and the form
    warning = 'Be careful! If you upload a new picture your last picture will be erased!'
    return render(request,
                  'imageModifier/uploadTransformableImage.html', {
                      'form': form, 'warning': warning, 'old_image_transf_builder': old_image_transf_builder,
                      'user_prop': user_prop}
                  )


def image_processing(request, user_proposition_pk):
    user_proposition = get_object_or_404(UserProposition, pk=user_proposition_pk)
    transformed_image_builder = user_proposition.transformedimagebuilder
    companyImagesList = user_proposition.company_proposition.campaign.company_logos.all()

    if request.method == 'POST':
        image_property_form = ImageProcessingParametersForm(request.POST, instance=transformed_image_builder)

        if image_property_form.is_valid():
            print('valid')
            new_transformed_image_builder = image_property_form.save(commit=False)
            new_transformed_image_builder.last_update_date = timezone.now()
            new_transformed_image_builder.save()
            new_transformed_image_builder.generate_intermediary_image()
            return HttpResponseRedirect(
                reverse('imageModifier:user_proposition_detail', kwargs={'user_proposition_pk': user_proposition_pk}))
        print('not valid form')
    else:
        image_property_form = ImageProcessingParametersForm(instance=transformed_image_builder)

    return render(request, 'imageModifier/image_processing.html',
                  {'image_property_form': image_property_form, 'user_proposition': user_proposition,
                   'transformedimagebuilder': transformed_image_builder,
                   'companyLogoList': companyImagesList})


def user_proposition_detail(request, user_proposition_pk):
    user_proposition = get_object_or_404(UserProposition, pk=user_proposition_pk)
    return render(request, 'imageModifier/user_proposition_detail.html',
                  {'user_proposition': user_proposition})


@login_required
def user_propositions_list(request):
    list_user_prop = UserProposition.objects.filter(worker_user=request.user).order_by('-creation_date')
    return render(request, 'imageModifier/user_propositions_list.html', {'list_user_prop': list_user_prop})


def worker_select_campaign(request):
    """
    Shows the list of company to select for the worker. Will run an auction and compute everything it needs.
    :param request:
    :return:
    """
    global error_message
    error_message = ''
    this_user = request.user
    user_details = this_user.user_details
    expired = True
    try:
        expired = user_details.last_auction.has_expired()
        print('Auction has been run before...')
    except AttributeError:
        print('First time in auction...')
        pass
    if not expired:
        auction = user_details.last_auction
        print('... and is not yet expired.')
    else:
        # The user has left the page without refresh during too long.
        if request.method == 'POST':
            error_message = "Sorry, the page has timed out. Please select a proposition again."
        # We are running a new auction here, creating it and saving it
        print('Creating auctions.')
        auction = Auction(worker_user=this_user, auction_date=timezone.now())
        auction.save()
        user_details.last_auction = auction
        user_details.save()

        # Creating the auction element and computing the score for each proposition
        for proposition in request.user.companyproposition_set.all():
            if not UserProposition.objects.filter(worker_user=this_user).filter(company_proposition=proposition):
                auction_elem = AuctionElement(auction=auction, company_proposition=proposition,
                                              bid=proposition.money_that_will_be_paid_per_worker)
                auction_elem.save()
                auction_elem.make_bid()

    # Making the form get the chosen auction element back.
    if request.method != 'POST':
        form = SelectAuctionElementForm()
    else:
        form = SelectAuctionElementForm(request.POST)  # get the form
        print('post')
        if form.is_valid():
            print('valid')
            pk_selected_auction = form.cleaned_data['select_auction_element']
            print(pk_selected_auction)
            # Try to find the element in the auction set that was generated before
            try:
                selected_auction_elem = auction.auctionelement_set.get(pk=pk_selected_auction)
            except ObjectDoesNotExist:
                pass
            else:
                if selected_auction_elem:
                    now = timezone.now()
                    new_user_proposition = UserProposition(worker_user=this_user, auction_element=selected_auction_elem,
                                                           company_proposition=selected_auction_elem.company_proposition,
                                                           creation_date=now, last_update_date=now)
                    try:
                        new_user_proposition.save()
                    except IntegrityError:
                        error_message = 'You have already selected this campaign. Please select an other campaign or go to past creations to modify it.'
                    else:
                        auction.has_been_used_once = True
                        auction.save()
                        print('auction element selected, user proposition created!')
                        return HttpResponseRedirect(reverse('imageModifier:uploadTransformableImage',
                                                            kwargs={'user_proposition_pk': new_user_proposition.pk}))
        else:
            # Form not valid, so no proposition selected.
            error_message = 'Please select a proposition before continuing.'

    return render(request, 'imageModifier/worker_select_campaign.html',
                  {'auction_elements': auction.auctionelement_set.order_by('-final_score'), 'form': form,
                   'error_message': error_message})
