from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import timedelta
import datetime
from regluit.core import models

num=0
start = datetime.datetime.now()
for work in models.Work.objects.all():
    try:
        id = work.identifiers.values('type', 'value').filter(type='goog')[0]['value']
    except IndexError:
        pass
    num += 1
    if num == 10000:
        break
end = datetime.datetime.now()
print "2 values "+str(end - start)

num=0
start = datetime.datetime.now()
for work in models.Work.objects.all():
    try:
        id = work.identifiers.filter(type='goog')[0].value
    except IndexError:
        pass
    num += 1
    if num == 10000:
        break
end = datetime.datetime.now()
print "orig "+str(end - start)

num=0
start = datetime.datetime.now()
for work in models.Work.objects.all():
    try:
        id = work.identifiers.values('value').filter(type='goog')[0]['value']
    except IndexError:
        pass
    num += 1
    if num == 10000:
        break
end = datetime.datetime.now()
print "1 value "+ str(end - start)

num=0
start = datetime.datetime.now()
for work in models.Work.objects.all():
    try:
        id = work.identifiers.values('type', 'value').filter(type='goog')[0]['value']
    except IndexError:
        pass
    num += 1
    if num == 10000:
        break
end = datetime.datetime.now()
print "2 values "+str(end - start)
