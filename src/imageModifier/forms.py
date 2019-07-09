from django import forms
from django.forms import ModelForm

from imageModifier.models import CompanyLogoImage, TransformedImageBuilder


class UploadImageForm(forms.Form):
    uploaded_image = forms.ImageField(label='Select an image to upload.', )


class SelectAuctionElementForm(forms.Form):
    select_auction_element = forms.IntegerField(required=True, widget=forms.HiddenInput())


class ImageProcessingParametersForm(ModelForm):
    class Meta:
        model = TransformedImageBuilder
        fields = ['company_logo', 'image_parameter_logo_width', 'image_parameter_logo_left_position',
                  'image_parameter_logo_top_position',
                  'image_parameter_base_image_ratio']
        widgets = {'company_logo': forms.HiddenInput(), 'image_parameter_logo_width': forms.HiddenInput(),
                   'image_parameter_logo_left_position': forms.HiddenInput(),
                   'image_parameter_logo_top_position': forms.HiddenInput(),
                   'image_parameter_base_image_ratio': forms.HiddenInput()}


class SelectUploadCampaignLogosForm(forms.Form):
    uploaded_image = forms.ImageField(required=False, label='Select an image to upload.', )
    logo_representative = forms.ModelChoiceField(required=False, queryset=None, empty_label=None)
    logos_to_deselect = forms.ModelMultipleChoiceField(required=False, queryset=None)
    logos_to_select = forms.ModelMultipleChoiceField(required=False, queryset=None)

    def __init__(self, this_company, this_campaign, *args, **kwargs):
        super(SelectUploadCampaignLogosForm, self).__init__(*args, **kwargs)
        self.fields['logos_to_select'].queryset = CompanyLogoImage.objects.filter(related_company=this_company).exclude(
            campaign=this_campaign)
        self.fields['logos_to_deselect'].queryset = this_campaign.company_logos.all()
        self.fields['logo_representative'].queryset = this_campaign.company_logos.all()
        self.fields['logo_representative'].initial = this_campaign.company_logo_representative
