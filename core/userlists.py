#put logic for retrieving userlists here

from django.contrib.auth.models import User
import random

def other_users(user, how_many):
    # do something more sophisitcated sometime later
    count = User.objects.all().count()
    if count <= how_many :
        user_list = User.objects.all()[0: count]
    else :
        slice = random.random() * (count - how_many)
        user_list = User.objects.all()[slice: slice+how_many]
    return user_list
