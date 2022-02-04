from django.contrib import admin

from .models import SesKey


class SesKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'ses_key']

admin.site.register(SesKey, SesKeyAdmin)
