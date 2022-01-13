from django.contrib import admin
from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'login', 'name', 'phone', 'variants', 'time_create', 'time_update')
    list_display_links = ('id', 'chat_id')
    search_fields = ('login', 'name', 'phone')
    list_filter = ('time_create',)
    fields = ('chat_id', 'login', 'name', 'phone', 'variants', 'time_create', 'time_update')
    readonly_fields = ('chat_id', 'login', 'name', 'phone', 'variants', 'time_create', 'time_update')


admin.site.register(Order, OrderAdmin)
