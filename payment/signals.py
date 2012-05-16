from django.dispatch import Signal

transaction_charged = Signal(providing_args=["transaction"])
