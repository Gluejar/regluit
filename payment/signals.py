from django.dispatch import Signal

transaction_charged = Signal(providing_args=["transaction"])
pledge_created = Signal(providing_args=["transaction"])
pledge_modified = Signal(providing_args=["transaction", "up_or_down"])