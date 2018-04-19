from django.utils.timezone import now

    
# switch to  django.utils.timezone.localdate in django 1.11

def date_today():
    return now().date()

