from django.contrib.admin import ModelAdmin, site
from .models import Transaction, PaymentResponse, Receiver

class TransactionAdmin(ModelAdmin):
    list_display = ('campaign', 'user', 'amount', 'status', 'error')
    date_hierarchy = 'date_created'
    
class PaymentResponseAdmin(ModelAdmin):
    pass

class ReceiverAdmin(ModelAdmin):
    ordering = ('email',)    
    
# payments

site.register(Transaction, TransactionAdmin)
site.register(PaymentResponse, PaymentResponseAdmin)
site.register(Receiver, ReceiverAdmin)
