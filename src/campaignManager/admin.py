from campaignManager.models import Campaign, CompanyProposition, AuctionElement, Auction, UserProposition
from django.contrib import admin


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('headline', 'company', 'created_by', 'last_update_date', 'creation_date', 'pk')
    list_filter = ['creation_date', 'last_update_date']
    search_fields = ['headline', 'company']


class CompanyPropositionAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'nb_of_people_accepted', 'money_that_will_be_paid_per_worker', 'last_modified_by',
        'last_update_date', 'creation_date', 'pk')
    list_filter = ['creation_date', 'last_update_date']
    search_fields = ['campaign', 'creation_date']


class UserPropositionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'worker_user', 'company_proposition', 'creation_date')
    list_filter = ['creation_date', 'company_proposition']


admin.site.register(Campaign, CampaignAdmin)

admin.site.register(CompanyProposition, CompanyPropositionAdmin)
admin.site.register(UserProposition, UserPropositionAdmin)
admin.site.register(Auction)
admin.site.register(AuctionElement)
