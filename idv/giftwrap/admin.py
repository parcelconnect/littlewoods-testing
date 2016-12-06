from django.contrib import admin

from .models import GiftWrapRequest


@admin.register(GiftWrapRequest)
class GiftWrapRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'account_number', 'upi', 'status', 'created_at'
    )
    list_filter = ['status']
