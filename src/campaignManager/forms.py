from django import forms
from django.forms import ModelForm, SelectDateWidget, CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe

from campaignManager.models import Campaign, CompanyProposition


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = ['headline', 'description', 'expiration_date', 'no_logo_campaign']
        widgets = {'expiration_date': SelectDateWidget}


class CompanyPropositionForm(ModelForm):
    class Meta:
        model = CompanyProposition
        fields = ['nb_of_people_accepted', 'money_that_will_be_paid_per_worker', 'nb_of_reserved_day',
                  'expiration_date', 'must_contain_link_to_website', 'minimum_logo_size_in_percentage_of_picture',
                  'allow_logo_to_go_out_of_frame', 'filter_nb_of_followers', 'filter_average_nb_of_like_in_10_last_pictures',
                  'filter_number_of_successful_past_collaborations', 'workers_selected']
        widgets = {'expiration_date': SelectDateWidget, 'workers_selected': CheckboxSelectMultiple}
        labels = {
            'filter_average_nb_of_like_in_10_last_pictures': _('Mean number of likes of the web stars'),
        }


        # class WorkersSelectedInFilter(forms.Form):
        #     workers_choices_field = forms.MultipleChoiceField(label='Web star choice ', widget=forms.CheckboxSelectMultiple)

        #
        #
        #
        #
        # class WorkerWithInformation(forms.models.MultipleChoiceField):
        #     def label_from_instance(self, obj):
        #         return mark_safe("<span>{}</span><span class=\"desc\" id=\"desc_{}\">{}</span>".format(smart_text(obj), obj.id, smart_text(obj.description),))
        #

        # class ExtraModelChoiceField(forms.models.ModelChoiceField):
        #
        #     def label_from_instance(self, obj):
        #         return mark_safe(
        #             "<span>%s</span><span class=\"desc\" id=\"desc_%s\">%s</span>" % (
        #             mart_unicode(obj), obj.id, smart_unicode(obj.description),))


        # class LocationForm(forms.Form):
        #     location = ExtraModelChoiceField(widget=forms.RadioSelect(renderer=HorizRadioRenderer),
        #         queryset=models.Location.objects.filter(active=True))
