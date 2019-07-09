from django.contrib import admin
from imageModifier.models import CompanyLogoImage, TransformedImageBuilder, TransformedImage


admin.site.register(TransformedImage)


class CompanyLogoImageAdmin(admin.ModelAdmin):
    list_display = ('pk','related_company','uploaded_by', 'companyImageUploaded', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['companyName']



class TransformedImageBuilderAdmin(admin.ModelAdmin):
    list_display = ('pk','user_proposition','base_image', 'last_update_date')
    list_filter = ['last_update_date']

admin.site.register(TransformedImageBuilder,TransformedImageBuilderAdmin)
admin.site.register(CompanyLogoImage, CompanyLogoImageAdmin)
