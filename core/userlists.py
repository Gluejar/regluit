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
    count = work.num_wishes
    if count <= how_many :
        user_list = work.wished_by()[0: count]
    else :
        slice = random.random() * (count - how_many)
        user_list = work.wished_by()[slice: slice+how_many]
    return user_list

def work_list_users(work_list, how_many):
    """return up to how_many users with one of the works on work_list in their wishlist"""
    #users = User.objects.filter(wishlist__works__in=work_list).distinct().reverse()
    # for MySQL, avoiding a nested query is more efficient: https://docs.djangoproject.com/en/dev/ref/models/querysets/#in
    users = User.objects.filter(wishlist__works__in=list(work_list[:100])).distinct().reverse()
    return users.all()[0:how_many]

def campaign_list_users(campaign_list, how_many):
    users = User.objects.filter(wishlist__works__campaigns__in=list(campaign_list[:100])).distinct().reverse()
    count = users.count()
    if count <= how_many :
        user_list = users[0: count]
    else :
        user_list = users[0: how_many]
    return user_list
