"""
https://github.com/agiliq/merchant/blob/master/example/app/integrations/fps_integration.py
"""

import billing
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
            # check to see whether we recognize this transaction -- correlate by callerReference
            callerReference = dd.get('callerReference')
            if callerReference is not None:
                try:
                    trans = billing.models.AmazonFPSResponse.objects.get(callerReference=callerReference)
                except billing.models.AmazonFPSResponse.DoesNotExist:
                    return HttpResponse('callerReference not recognized')
                except Exception, e:
                    logger.exception("Error: {0}".format(e))
                    return HttpResponse('Error: {0}'.format(e))
            else:
                logger.warning('no callerReference included')
                return HttpResponse('no callerReference included')
                
            try:
                transactionAmount = trans.transactionAmount
                # should also have stored in the database that this is a purchase....
                logger.info('transactionAmount: {0}; dd:{1}'.format(transactionAmount, dd))
                resp = self.purchase(transactionAmount, dd)
            except Exception, e:
                logger.exception("Error: {0}".format(e))
                return HttpResponse('Error: {0}'.format(e))
                
            # resp: status representing the status and response representing the response as described by boto.fps.response.FPSResponse.
            # mystery stuff with https://github.com/boto/boto/blob/develop/boto/resultset.py and
            #  https://github.com/boto/boto/blob/develop/boto/fps/response.py
            
            #In [17]: resp['response'].RequestId
            #Out[17]: u'1f7b74a5-977a-4ffe-9436-d3c0203a6a85:0'
            #
            #In [18]: resp['response'].TransactionId
            #Out[18]: u'16QVZ98TK48G3AK2QR1N1JJN8TLPE41R3NU'
            #
            #In [19]: resp['response'].TransactionStatus
            #Out[19]: u'Pending'
            #
            #In [20]: resp['status']
            #Out[20]: u'Pending'
            #
            #In [21]: resp['response'].PayResult
            #Out[21]: ''
            #
            #In [22]: resp['response'].PayResponse
            #Out[22]: ''
            #
            #In [23]: resp['response'].connection
            #Out[23]: FPSConnection:fps.sandbox.amazonaws.com

            # Now process the response
            
            trans.transactionId = resp['response'].TransactionId
            trans.transactionStatus = resp['response'].TransactionStatus
            trans.save()
            
            logger.debug("transactionId: {0}, transactionStatus: {1}".format(trans.transactionId, trans.transactionStatus ))
            
            
            return HttpResponseRedirect("%s?status=%s" %(reverse("testfps"),
                                resp["status"]))
        elif dd.get('status') == 'A':
            return HttpResponse('You cancelled the transaction')
        else:
            return HttpResponse('An unexpected status code: {0}'.format(dd.get('status')))
            