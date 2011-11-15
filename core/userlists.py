#put logic for retrieving userlists here

import random
from django.contrib.auth.models import User
from regluit.core.models import Work

def other_users(user, how_many):
    # do something more sophisitcated sometime later
    count = User.objects.all().count()
    if count <= how_many :
        user_list = User.objects.all()[0: count]
    else :
        slice = random.random() * (count - how_many)
        user_list = User.objects.all()[slice: slice+how_many]
    return user_list

def supporting_users(work, how_many):
    # do something more sophisitcated sometime later
    count = work.wished_by().count()
    if count <= how_many :
        user_list = work.wished_by()[0: count]
    else :
        slice = random.random() * (count - how_many)
        user_list = work.wished_by()[slice: slice+how_many]
    return user_list
