import decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from aiaUsers.models import Company, WorkerUserDetails


# ------------------------------ Validators ------------------------------#
from imageModifier.models import CompanyLogoImage


def validate_percentage_logo_size(value):
    if value > CompanyProposition.MAX_LOGO_SIZE_IN_PERCENTAGE or value < CompanyProposition.MIN_LOGO_SIZE_IN_PERCENTAGE:
        raise ValidationError(_('Please enter a value between 0 and 1.'), params={'value': value}, )


class Campaign(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    company_logos = models.ManyToManyField(CompanyLogoImage)
    company_logo_representative = models.ForeignKey(CompanyLogoImage, blank=True, null=True, on_delete=models.SET_NULL,
                                                    related_name='logo_representative')
    headline = models.CharField(max_length=140, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    no_logo_campaign = models.BooleanField(default=False, blank=True, null=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name="%(app_label)s_%(class)s_created_by")
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                         related_name="%(app_label)s_%(class)s_last_modified_by")
    creation_date = models.DateTimeField(null=False)
    last_update_date = models.DateTimeField('last update', null=False)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.headline) + ";  company = " + str(self.company)

    def get_nb_of_company_proposition(self):
        return CompanyProposition.objects.filter(campaign=self).count()


class CompanyProposition(models.Model):
    MIN_LOGO_SIZE_IN_PERCENTAGE = 0
    MAX_LOGO_SIZE_IN_PERCENTAGE = 1

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    workers_selected = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    nb_of_people_accepted = models.IntegerField(null=False, blank=False)
    money_that_will_be_paid_per_worker = models.DecimalField(max_digits=19, decimal_places=4, null=False, blank=False)
    creation_date = models.DateTimeField(null=False, blank=False)
    last_update_date = models.DateTimeField('last update', null=False, blank=False)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                         related_name="%(app_label)s_%(class)s_last_modified_by")
    expiration_date = models.DateTimeField(null=True, blank=True)
    nb_of_reserved_day = models.IntegerField(default=0, null=False, blank=False)
    must_contain_link_to_website = models.BooleanField(default=False)
    allow_logo_to_go_out_of_frame = models.BooleanField(default=False)
    minimum_logo_size_in_percentage_of_picture = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True,
                                                                     default=MIN_LOGO_SIZE_IN_PERCENTAGE,
                                                                     validators=[validate_percentage_logo_size])
    filter_nb_of_followers = models.IntegerField(null=True, blank=True, default=0)
    filter_average_nb_of_like_in_10_last_pictures = models.IntegerField(null=True, blank=True, default=0)
    filter_number_of_successful_past_collaborations = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return str(self.campaign) + ", CHF " + str(self.money_that_will_be_paid_per_worker) + " and " + str(
            self.nb_of_people_accepted) + " workers."


class UserProposition(models.Model):
    worker_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    auction_element = models.OneToOneField('AuctionElement', on_delete=models.SET_NULL, null=True)
    company_proposition = models.ForeignKey(CompanyProposition, on_delete=models.SET_NULL, null=True)
    # transformed_image = models.OneToOneField(TransformedImageBuilder, on_delete=models.CASCADE, null=True, blank=True)
    creation_date = models.DateTimeField()
    last_update_date = models.DateTimeField('last update', null=False, blank=False)
    expiration_date = models.DateTimeField(null=True, blank=True)
    can_propose = models.BooleanField(default=True, null=False)
    has_sent_proposition = models.BooleanField(default=False, null=False)
    proposition_accepted = models.BooleanField(default=False, null=False)

    def __str__(self):
        return "User proposition " +str(self.pk) + " from " + str(self.worker_user) + ", for : " + str(self.company_proposition)


class Auction(models.Model):
    DURATION_BEFORE_EXPIRATION_IN_SECOND = 8

    worker_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    auction_date = models.DateTimeField(auto_now_add=True)
    has_been_used_once = models.BooleanField(default=False)

    def has_expired(self):
        time_diff = timezone.now() - self.auction_date
        return self.has_been_used_once or (time_diff.seconds >= self.DURATION_BEFORE_EXPIRATION_IN_SECOND)

    def __str__(self):
        return "Auction for " + str(self.worker_user) + ", with " + str(self.auctionelement_set.count()) + " propositions."


class AuctionElement(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, null=False)
    company_proposition = models.ForeignKey(CompanyProposition, on_delete=models.SET_NULL, null=True)
    bid = models.DecimalField(max_digits=19, decimal_places=4, null=False, blank=False)
    company_quality_score = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    campaign_quality_score = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    fitting_quality_score = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    final_quality_score = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    final_score = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    final_payment = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    # relative_position = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-final_score']

    def __str__(self):
        return "AuctionElement with bid = " + str(self.bid) + ", final score=" + str(self.final_score) + " and payment=" + str(
            self.final_payment)

    def make_bid(self):
        print('\n\nPrinting scores of company:  "{}", campaign #{}...'.format(self.company_proposition.campaign.company.name,
                                                                              self.company_proposition.campaign.pk))
        self.compute_scores()
        self.__compute_payment()
        print('Final quality score = {:.3f}, and Final score = {:.3f}'.format(self.final_quality_score, self.final_score))
        print('Bid = {:.2f}'.format(self.bid))
        print('-------------------------------------------------------------------')

    def compute_scores(self):
        """
        Compute the final score of the company using the bid and the quality functions.
        Compute the quality function.
        :return:
        """
        self.__compute_quality_score()
        self.final_score = self.bid * decimal.Decimal(self.final_quality_score)
        self.save()

    def __compute_quality_score(self):
        MAX_QUALITY_SCORE = 10
        MIN_QUALITY_SCORE = 0
        FACTOR_COMPANY_QUALITY = 0.3
        FACTOR_CAMPAIGN_QUALITY = 0.3
        FACTOR_FITTING_QUALITY = 0.4
        AuctionElement.__check_correctness_quality_score_parameters(FACTOR_COMPANY_QUALITY, FACTOR_CAMPAIGN_QUALITY,
                                                                    FACTOR_FITTING_QUALITY)

        company_quality_score = self.__compute_company_quality_score()
        campaign_quality_score = self.__compute_campaign_quality_score()
        fitting_quality_score = self.__compute_fitting_quality_score()

        self.final_quality_score = company_quality_score * FACTOR_COMPANY_QUALITY + campaign_quality_score * FACTOR_CAMPAIGN_QUALITY
        self.final_quality_score = self.final_quality_score * (MAX_QUALITY_SCORE - MIN_QUALITY_SCORE) + MIN_QUALITY_SCORE

        self.campaign_quality_score = campaign_quality_score
        self.company_quality_score = company_quality_score
        self.save()

    def __compute_fitting_quality_score(self):
        print('Computing fitting quality score...')
        MAX_FILTER_SIZE = 50  # the filter does not target specific people anymore
        FACTOR_FILTER_SIZE = 1
        AuctionElement.__check_correctness_quality_score_parameters(FACTOR_FILTER_SIZE)
        filter_size = self.company_proposition.workers_selected.count()
        print('filter size={}'.format(filter_size))

        # Percent parameters calculation
        filter_percent = 1 - min(filter_size, MAX_FILTER_SIZE) / MAX_FILTER_SIZE
        AuctionElement.__check_value_is_percentage(filter_percent)
        print('filter_percent={:.1%}'.format(filter_percent))


        # Computation with the factor
        filter_percent *= FACTOR_FILTER_SIZE
        print('filter_percent={:.1%}'.format(filter_percent))

        # Overall quality computation
        fitting_quality_score = filter_percent
        AuctionElement.__check_value_is_percentage(fitting_quality_score)
        print('fitting_quality_score = {:.1%}\n'.format(fitting_quality_score))
        return fitting_quality_score

    def __compute_campaign_quality_score(self):
        """
        Determine if the campaign is of good quality.
        :return: a value between 0 and 1
        """
        print('Computing campaign quality score...')
        IDEAL_MIN_LOGO_NB = 3
        IDEAL_MIN_DESCR_LENGTH = 140
        FACTOR_NB_LOGO = 0.4
        FACTOR_DESCR_LENGHT = 0.4
        FACTOR_PROPOSITION_IS_ENDING = 1 - FACTOR_NB_LOGO - FACTOR_DESCR_LENGHT
        AuctionElement.__check_correctness_quality_score_parameters(FACTOR_NB_LOGO, FACTOR_DESCR_LENGHT,
                                                                    FACTOR_PROPOSITION_IS_ENDING)

        # Percent parameters calculation
        campaign = self.company_proposition.campaign
        prop_ending = 0
        descr_percent = 0
        logo_percent = min(campaign.company_logos.count(), IDEAL_MIN_LOGO_NB) / IDEAL_MIN_LOGO_NB

        # descr_percent calculation : if campaign description exists
        try:
            description = campaign.description
        except AttributeError:
            pass
        else:
            descr_percent = min(len(description), IDEAL_MIN_DESCR_LENGTH) / IDEAL_MIN_DESCR_LENGTH


        # prop_ending calculation: check if expiration date exists
        now = timezone.now()
        creation = campaign.creation_date
        try:
            expiration = campaign.expiration_date
        except AttributeError:
            pass
        else:
            if expiration and creation < now < expiration:
                prop_ending = (now - creation) / (expiration - creation)
        AuctionElement.__check_value_is_percentage(prop_ending, descr_percent, logo_percent)
        print('logo_percent={:.1%}, descr_percent={:.1%}, prop_ending={:.1%}'.format(logo_percent, descr_percent, prop_ending))

        # Computation with the factors
        logo_percent *= FACTOR_NB_LOGO
        descr_percent *= FACTOR_DESCR_LENGHT
        prop_ending *= FACTOR_PROPOSITION_IS_ENDING
        print('logo_percent={:.1%}, descr_percent={:.1%}, prop_ending={:.1%}'.format(logo_percent, descr_percent, prop_ending))

        # Overall quality computation
        campaign_quality_score = logo_percent + descr_percent + prop_ending
        print('campaign_quality_score = {:.1%}\n'.format(campaign_quality_score))
        return campaign_quality_score

    def __compute_company_quality_score(self):
        """
        This will compute the score of the company.
        It will return a value between 0 and 1 which is the ideal quality
        :return:
        """
        INITIAL_QUALITY_SCORE = 0
        MINIMUM_SUCCESS_TO_HAVE_EXPERIENCE = 5

        FACTOR_SUCCESSFUL_COLABORATIONS = 0.3
        FACTOR_NO_EXPLANATION_REJECTION = 0.5
        FACTOR__MINIMUM_EXPERIENCE = 1 - FACTOR_NO_EXPLANATION_REJECTION - FACTOR_SUCCESSFUL_COLABORATIONS
        AuctionElement.__check_correctness_quality_score_parameters(FACTOR_NO_EXPLANATION_REJECTION, FACTOR__MINIMUM_EXPERIENCE,
                                                                    FACTOR_SUCCESSFUL_COLABORATIONS)
        print('Computing company quality score...')
        company = self.company_proposition.campaign.company
        tot_image = company.nb_of_worker_image_proposed
        nb_success = company.number_of_successful_past_collaboration
        if tot_image == 0:
            company_quality_score = INITIAL_QUALITY_SCORE
        else:

            # Percent parameters calculation
            success = (nb_success / tot_image)
            not_reject_no_explanation = 1 - (company.nb_of_worker_image_rejected_with_no_explanation / tot_image)
            experienced = min(nb_success, MINIMUM_SUCCESS_TO_HAVE_EXPERIENCE) / MINIMUM_SUCCESS_TO_HAVE_EXPERIENCE
            AuctionElement.__check_value_is_percentage(success, not_reject_no_explanation, experienced)
            print(
                'not_reject_no_explanation={:.1%}, success={:.1%}, experienced={:.1%}'.format(not_reject_no_explanation, success,
                                                                                              experienced))

            # Computation with the factors
            success *= FACTOR_SUCCESSFUL_COLABORATIONS
            not_reject_no_explanation *= FACTOR_NO_EXPLANATION_REJECTION
            experienced *= FACTOR__MINIMUM_EXPERIENCE
            print(
                'not_reject_no_explanation={:.1%}, success={:.1%}, experienced={:.1%}'.format(not_reject_no_explanation, success,
                                                                                              experienced))

            # Overall quality computation
            company_quality_score = success + not_reject_no_explanation + experienced
            AuctionElement.__check_value_is_percentage(company_quality_score)
        print('company_quality_score = {:.1%}\n'.format(company_quality_score))
        return company_quality_score

    @staticmethod
    def __check_correctness_quality_score_parameters(*values):
        """
        Check if the parameter are percentages, and if their sum is of 1
        :param values: the parameter to check
        :raise an exception if they are not correct
        """
        AuctionElement.__check_value_is_percentage(*values)
        my_sum = 0
        for val in values:
            my_sum += val
        if not my_sum == 1:
            raise ValidationError('The parameter sum is not 1. Sum=' + str(my_sum))

    @staticmethod
    def __check_value_is_percentage(*values):
        for val in values:
            if not (0 <= val <= 1):
                raise ValidationError('Value is not a percentage, it is >1 or <0. Value = ' + str(val))

    def __compute_payment(self):
        self.final_payment = self.bid
        self.save()
