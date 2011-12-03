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
    # do something more sophisticated sometime later
    count = work.wished_by().count()
    if count <= how_many :
        user_list = work.wished_by()[0: count]
    else :
        slice = random.random() * (count - how_many)
        user_list = work.wished_by()[slice: slice+how_many]
    return user_list

def work_list_users(work_list, how_many):
    users = User.objects.filter(wishlist__works__in=work_list).distinct().reverse()
    count = users.count()
    if count <= how_many :
        user_list = users[0: count]
    else :
        user_list = users[0: how_many]
    return user_list

def campaign_list_users(campaign_list, how_many):
    users = User.objects.filter(wishlist__works__campaigns__in=campaign_list).distinct().reverse()
    count = users.count()
    if count <= how_many :
        user_list = users[0: count]
    else :
        user_list = users()[0: how_many]
    return user_list
