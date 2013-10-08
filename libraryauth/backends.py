import logging
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Block, IP

logger = logging.getLogger(__name__)

def ip_authenticate(request, library):
    try:
        ip = IP(request.META['REMOTE_ADDR'])
        print str(ip)
        blocks = Block.objects.filter(Q(lower=ip) | Q(lower__lte=ip, upper__gte=ip))
        for block in blocks:
            if block.library==library:
                logger.info('%s authenticated for %s from %s'%(request.user, library, ip))
                return True
        return False
    except KeyError:
        return False
     
def ip_authenticator(request, library, success_url, deny_url):
    return HttpResponseRedirect(deny_url)
    
def cardnum_authenticate(request, library):
    # test params
    return True

def cardnum_authenticator(request, library, success_url, deny_url):
    #send a form
    return render(request, 'cardnum.html', context)
