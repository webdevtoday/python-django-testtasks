from django.contrib import admin
from .models import *


class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'referral_id', 'user_id',
                    'username', 'time_create', 'time_update')
    list_display_links = ('id', 'referral_id')
    search_fields = ('referral_id', 'user_id', 'username')
    list_filter = ('time_create',)
    fields = ('referral_id', 'user_id', 'username',
              'time_create', 'time_update')
    readonly_fields = ('time_create', 'time_update')


admin.site.register(Users, UsersAdmin)
