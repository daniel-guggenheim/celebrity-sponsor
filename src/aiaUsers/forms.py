from aiaUsers.models import UserDetails, BaseUserDetails
from django import forms
from django.utils import timezone

COMPANY_NUM = BaseUserDetails.COMPANY_VAL
WORKER_NUM = BaseUserDetails.WORKER_VAL


class DetailsSignupForm(forms.Form):
    CHOICES = ((COMPANY_NUM, 'A company',), (WORKER_NUM, 'A celebrity',))
    choice_field = forms.ChoiceField(label='I am ', widget=forms.RadioSelect, choices=CHOICES, required=True)

    def signup(self, request, user):
        choice = self.cleaned_data['choice_field']
        int_choice = int(choice)

        if int_choice == COMPANY_NUM or int_choice == WORKER_NUM:
            user_detail = UserDetails(linked_user=user, user_type=int_choice, creation_date=timezone.now())
            print('User created: ' + str(user_detail))
            user.save()
            user_detail.save()
        else:
            print('user creation failure: bad category choice')
