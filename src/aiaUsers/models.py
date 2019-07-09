from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import DateTimeField


# TODO: Change on_delete method of Company 'created_by' attribute
class Company(models.Model):
    name = models.CharField(max_length=300)
    abrev_name = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    number_of_successful_past_collaboration = models.IntegerField(default=0, null=False, blank=True)
    nb_of_worker_image_rejected_with_no_explanation = models.IntegerField(default=0, null=False, blank=True)
    nb_of_worker_image_proposed = models.IntegerField(default=0, null=False, blank=True)

    def get_absolute_url(self):
        reverse('aiaUsers:company_details')

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return "{0}".format(self.name)

    def get_nb_of_worker_image_rejected(self):
        return self.nb_of_worker_image_proposed - self.number_of_successful_past_collaboration


class BaseUserDetails(models.Model):
    COMPANY_VAL = 0
    WORKER_VAL = 1
    ALL_VAL = 2
    NONE_VAL = 3
    ANONYMOUS_USER_VAL = 4

    USER_TYPES = (
        (COMPANY_VAL, 'Company'),
        (WORKER_VAL, 'Worker'),
        (ALL_VAL, 'All'),
        (NONE_VAL, 'None'),
    )
    linked_user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='user_details')
    user_type = models.IntegerField(null=True, choices=USER_TYPES)
    creation_date = DateTimeField()
    # birth_date = models.DateField()

    class Meta:
        abstract = True

    def __str__(self):
        user_type_string = self.USER_TYPES[self.user_type][1]
        return "[{0}] - profile type: {1}".format(self.linked_user, user_type_string)

    def is_company_user_self(self):
        return self.__is_some_type_user_self(self.COMPANY_VAL)

    def is_worker_user_self(self):
        return self.__is_some_type_user_self(self.WORKER_VAL)

    def is_all_user_self(self):
        return self.__is_some_type_user_self(self.ALL_VAL)

    def __is_some_type_user_self(self, this_code):
        """
        Return boolean saying if the user is of the parameter type.
        :param this_code: the code corresponding to the users types
        :return: true if the user is of the type of the code
        """
        return self.user_type == this_code or self.user_type == self.ALL_VAL

    @staticmethod
    def is_company_user(this_user):
        return BaseUserDetails.__is_some_type_user(this_user, BaseUserDetails.COMPANY_VAL)

    @staticmethod
    def is_worker_user(this_user):
        return BaseUserDetails.__is_some_type_user(this_user, BaseUserDetails.WORKER_VAL)

    @staticmethod
    def __is_some_type_user(this_user, this_code):
        """
        Return true if the user is of the user code type.
        :param this_user: the user
        :param this_code: the code type of the user. See the class static variables to know the codes.
        :return:
        """
        try:
            this_user_detail = this_user.user_details
        except AttributeError:
            return this_code == BaseUserDetails.ANONYMOUS_USER_VAL
        else:
            return this_user_detail.__is_some_type_user_self(this_code)


class CompanyUserDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def global_has_a_company(this_user):
        try:
            det = this_user.user_details
            return det.has_a_company()
        except AttributeError:
            return False

    def has_a_company(self):
        try:
            comp = self.company
            return comp is not None
        except AttributeError:
            print('Testing usage: company is null or does not exist! Should redirect to add company')
            return False


class WorkerUserDetails(models.Model):
    NONE = 0
    SPORT = 1
    PHOTOGRAPHY = 2
    BAND = 3
    MUSIC = 4
    FASHION = 5
    MOVIE = 6
    FOOD = 7

    CATEGORY = (
        (NONE, 'none'),
        (SPORT, 'sport'),
        (PHOTOGRAPHY, 'photography'),
        (BAND, 'band'),
        (MUSIC, 'music'),
        (FASHION, 'fashion'),
        (MOVIE, 'movie'),
        (FOOD, 'food')
    )
    description = models.CharField(max_length=400, blank=True, null=True)
    last_auction = models.ForeignKey('campaignManager.Auction', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.IntegerField(null=True, blank=True, choices=CATEGORY)
    nb_of_followers_at_last_check = models.IntegerField(null=True,blank=True, default=0)
    average_nb_of_like_in_10_last_pictures_at_last_check = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    number_of_successful_past_collaborations = models.IntegerField(null=True, blank=True, default=0)
    last_check_social_media_information = models.DateTimeField(null=True, blank=True)


    class Meta:
        abstract = True

    def get_category_name(self):
        return self.CATEGORY(self.category)
    category_text = property(get_category_name)


class UserDetails(BaseUserDetails, CompanyUserDetails, WorkerUserDetails):
    pass

    class Meta:
        verbose_name_plural = "user details"

# TODO : Check if I keep this creation. ====> NO!! ;)
# User.details = property(lambda u: UserDetails.objects.get_or_create(user=u)[0])
