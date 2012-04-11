"""
https://github.com/agiliq/merchant/blob/master/example/app/integrations/fps_integration.py
"""

from billing.integrations.amazon_fps_integration import AmazonFpsIntegration as Integration
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
import urlparse

import logging
logger = logging.getLogger(__name__)


class FpsIntegration(Integration):
    def transaction(self, request):
        """Ideally at this method, you will check the 
        caller reference against a user id or uniquely
        identifiable attribute (if you are already not 
        using it as the caller reference) and the type 
        of transaction (either pay, reserve etc). For
        the sake of the example, we assume all the users
        get charged $100"""
        request_url = request.build_absolute_uri()
        parsed_url = urlparse.urlparse(request_url)
        query = parsed_url.query
        
        dd = dict(map(lambda x: x.split("="), query.split("&")))
        
        logger.info("dd: {0}".format(dd))
        
# dd: {'status': 'SC', 'signatureVersion': '2',
#     'tokenID': 'CLDITXQAX2DM82CT184S5CDNKYDXEPXETZ5QJFKB8AX4V9ZD34BGGJ6IDNFZDSUU',
#     'certificateUrl': 'https%3A%2F%2Ffps.sandbox.amazonaws.com%2Fcerts%2F090911%2FPKICert.pem%3FrequestId%3Dbjzj0zgbg2uf2j46a1iq123b9rwzl694mvpstlw1p5il426x7ap',
#     'expiry': '10%2F2017', 'signatureMethod': 'RSA-SHA1', 'callerReference': '5e0f7b0d-5cc5-4a55-a646-c6e420dd0f11',
#     'signature': 'Cc64A8DP7VclFBrhFEDXr2yhP8LaJpaLC6n%2F5oXiAhhD%2BnjJH9jQRhwPgB%2BuRvdcObMmZTD9we9G%0AvmEAkd5NkVULESdipsW%2B4i62mtD0DseuAtotMzjqObEeekzkaz4Vo0X9xcdlytLR04aEb4xqsLtg%0AJU%2Fysy7KStRivTqKzug%3D'}        

        # need to act based on status
        # getting status=SC, which doesn't seem to be in the documentation -- the docs say "SR":
        # http://docs.amazonwebservices.com/AmazonFPS/latest/FPSAdvancedGuide/CBUIapiMerchant.html
        # status = SC/SR, A, CE, NP, NM
        
        if dd.get('status') in ['SC', 'SR']:
            resp = self.purchase(100, dd)
            return HttpResponseRedirect("%s?status=%s" %(reverse("testfps"),
                                resp["status"]))
        elif dd.get('status') == 'A':
            return HttpResponse('You canceled the transaction')
        else:
            return HttpResponse('An unexpected status code: {0}'.format(dd.get('status')))
            