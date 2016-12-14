from django.contrib import admin

from .models import SftpAccount


@admin.register(SftpAccount)
class SftpAccountAdmin(admin.ModelAdmin):
    pass
