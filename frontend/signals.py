from django.dispatch import Signal

supporter_message = Signal(providing_args=["supporter", "work", "msg"])
