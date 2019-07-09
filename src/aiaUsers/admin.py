from aiaUsers.models import UserDetails, Company
from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')


class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('linked_user', 'user_type', 'creation_date')
    list_filter = ['user_type', 'creation_date']


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'abrev_name', 'created_by')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserDetails, UserDetailsAdmin)
admin.site.register(Company, CompanyAdmin)
