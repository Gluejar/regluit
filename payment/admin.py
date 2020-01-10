from django.contrib.admin import ModelAdmin, site
from .models import Transaction, PaymentResponse, Receiver, Account

class TransactionAdmin(ModelAdmin):
    list_display = ('campaign', 'user', 'amount', 'status', 'error')
    date_hierarchy = 'date_created'
    
class PaymentResponseAdmin(ModelAdmin):
    pass

class ReceiverAdmin(ModelAdmin):
    ordering = ('email',)    
    
def deactivate(modeladmin, request, queryset):
    for obj in queryset:
        obj.deactivate()

class AccountAdmin(ModelAdmin):
    search_fields = ('user__username', 'user__email',)
    list_display = ('user', 'card_type', 'card_exp_year',  'status')
    readonly_fields = ('user', 'card_type', 'card_last4', 'card_exp_month', 'card_exp_year', 
                      'date_created', 'date_modified', 'date_deactivated', 'status')
    fields = readonly_fields 
    actions = [deactivate]

    def deactivate(self, request, queryset):
        for obj in queryset:
            obj.deactivate()

# payments

site.register(Transaction, TransactionAdmin)
site.register(PaymentResponse, PaymentResponseAdmin)
site.register(Receiver, ReceiverAdmin)
site.register(Account, AccountAdmin)
