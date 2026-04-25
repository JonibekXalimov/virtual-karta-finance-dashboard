from django.contrib import admin

from .models import Transaction, VirtualCard


@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    list_display = ("user", "masked_number", "starting_balance", "created_at")
    search_fields = ("user__username", "card_number")
    readonly_fields = ("card_number", "created_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "note")
    ordering = ("-created_at",)
