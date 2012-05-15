from regluit.payment.parameters import *
from django.core.urlresolvers import reverse
from django.conf import settings
from regluit.payment.models import Transaction, PaymentResponse
from boto.fps.connection import FPSConnection
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from datetime import timedelta
from regluit.utils.localdatetime import now, zuluformat
from boto import handler
from boto.resultset import ResultSet
from boto.exception import FPSResponseError
import xml.sax

import traceback
import datetime
import logging
import urlparse
import time
import urllib

logger = logging.getLogger(__name__)

AMAZON_STATUS_SUCCESS_ABT = 'SA'
AMAZON_STATUS_SUCCESS_ACH = 'SB'
AMAZON_STATUS_SUCCESS_CREDIT = 'SC'
AMAZON_STATUS_ERROR = 'SE'
AMAZON_STATUS_ADBANDONED = 'A'
AMAZON_STATUS_EXCEPTION = 'CE'
AMAZON_STATUS_PAYMENT_MISMATCH = 'PE'
AMAZON_STATUS_INCOMPLETE = 'NP'
AMAZON_STATUS_NOT_REGISTERED = 'NM'

AMAZON_STATUS_CANCELED = 'Canceled'
AMAZON_STATUS_FAILURE = 'Failure'
AMAZON_STATUS_PENDING = 'Pending'
AMAZON_STATUS_RESERVED = 'Reserved'
AMAZON_STATUS_SUCCESS = 'Success'

AMAZON_IPN_STATUS_CANCELED = 'CANCELED'
AMAZON_IPN_STATUS_FAILURE = 'FAILURE'
AMAZON_IPN_STATUS_PENDING = 'PENDING'
AMAZON_IPN_STATUS_RESERVED = 'RESERVED'
AMAZON_IPN_STATUS_SUCCESS = 'SUCCESS'

AMAZON_NOTIFICATION_TYPE_STATUS = 'TransactionStatus'
AMAZON_NOTIFICATION_TYPE_CANCEL = 'TokenCancellation'

AMAZON_OPERATION_TYPE_PAY = 'PAY'
AMAZON_OPERATION_TYPE_REFUND = 'REFUND'
AMAZON_OPERATION_TYPE_CANCEL = 'CANCEL'

# load FPS_ACCESS_KEY and FPS_SECRET_KEY from the database if possible

try:
    from regluit.core.models import Key
    FPS_ACCESS_KEY = Key.objects.get(name="FPS_ACCESS_KEY").value
    FPS_SECRET_KEY = Key.objects.get(name="FPS_SECRET_KEY").value
    logger.info('Successful loading of FPS_*_KEYs')
except Exception, e:
    FPS_ACCESS_KEY = 'AKIAJMSHBCEKIDAHKIUQ'
    FPS_SECRET_KEY = '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'
    logger.info('EXCEPTION: unsuccessful loading of FPS_*_KEYs: {0}'.format(e))

def get_ipn_url():

    if settings.IPN_SECURE_URL:
        return settings.BASE_URL_SECURE + reverse('HandleIPN', args=["amazon"])
    else:
        return settings.BASE_URL + reverse('HandleIPN', args=["amazon"])

def ProcessIPN(request):
    '''
        IPN handler for amazon.  Here is a litle background on amazon IPNS
        http://docs.amazonwebservices.com/AmazonFPS/latest/FPSAdvancedGuide/APPNDX_IPN.html
        
        notificationType: Can either be TransactionStatus of TokenCancellation
        status: One of the defined IPN status codes
        operation: The type of operation
        callerReference: The reference to find the transaction
        
        The IPN is called for the following cases:
        
            A payment or reserve succeeds
            A payment or reserve fails
            A payment or reserve goes into a pending state
            A reserved payment is settled successfully
            A reserved payment is not settled successfully
            A refund succeeds    
            A refund fails
            A refund goes into a pending state    
            A payment is canceled
            A reserve is canceled    
            A token is canceled successfully
        
    '''
    try:
        logging.debug("Amazon IPN called")
        logging.debug(request.POST)
        
        uri = request.build_absolute_uri()
        parsed_url = urlparse.urlparse(uri)
        
        connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
        
        # Check the validity of the IPN
        resp = connection.verify_signature("%s://%s%s" %(parsed_url.scheme, 
                                                         parsed_url.netloc, 
                                                         parsed_url.path),
                                                         request.raw_post_data)
        
        if not resp[0].VerificationStatus == "Success":
            # Error, ignore this IPN
            logging.error("Amazon IPN cannot be verified with post data: ")
            logging.error(request.raw_post_data)
            return HttpResponseForbidden()
        
        logging.debug("Amazon IPN post data:")
        logging.debug(request.POST)

        reference = request.POST['callerReference']
        type = request.POST['notificationType']
        
        # In the case of cancelling a token, there is no transaction, so this info is not set
        transactionId = request.POST.get('transactionId', None)
        date = request.POST.get('transactionDate', None)
        operation = request.POST.get('operation', None)
        status = request.POST.get('transactionStatus', None)
        
        logging.info("Received Amazon IPN with the following data:")
        logging.info("type = %s" % type)
        logging.info("operation = %s" % operation)
        logging.info("reference = %s" % reference)
        logging.info("status = %s" % status)
        
        # We should always find the transaction by the token
        transaction = Transaction.objects.get(secret=reference)
        
        if type == AMAZON_NOTIFICATION_TYPE_STATUS:
            
            
            # status update for the token, save the actual value
            transaction.local_status = status
            
            # Now map our local status to the global status codes
            if operation == AMAZON_OPERATION_TYPE_PAY:
               
                
                if status == AMAZON_IPN_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_COMPLETE
                    
                elif status == AMAZON_IPN_STATUS_PENDING:
                    
                    if transaction.status == TRANSACTION_STATUS_CREATED:
                        #
                        # Per the amazon documentation:
                        # If your IPN receiving service is down for some time, it is possible that our retry mechanism will deliver the IPNs out of order.
                        # If you receive an IPN for TransactionStatus (IPN), as SUCCESS or FAILURE or RESERVED, 
                        # then after that time ignore any IPN that gives the PENDING status for the transaction
                        #
                        transaction.status = TRANSACTION_STATUS_PENDING
                else:
                    transaction.status = TRANSACTION_STATUS_ERROR
                
            elif operation == AMAZON_OPERATION_TYPE_REFUND:
                
                if status == AMAZON_IPN_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_REFUNDED
                elif status == AMAZON_IPN_STATUS_PENDING:
                    transaction.status = TRANSACTION_STATUS_PENDING
                else:
                    transaction.status = TRANSACTION_STATUS_ERROR
                    
            elif operation == AMAZON_OPERATION_TYPE_CANCEL:
                
                if status == AMAZON_IPN_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_COMPLETE
                else:
                    transaction.status = TRANSACTION_STATUS_ERROR
                 
                    
        elif type == AMAZON_NOTIFICATION_TYPE_CANCEL:
            #
            # The cancel IPN does not have a transaction ID or transaction status, so make them up
            #
            transaction.local_status = AMAZON_IPN_STATUS_CANCELED
            transaction.status = TRANSACTION_STATUS_CANCELED
            status = AMAZON_IPN_STATUS_CANCELED
            
        
        transaction.save()

        #
        # This is currently not done in paypal land, but log this IPN since the amazon IPN has good info
        #
        PaymentResponse.objects.create(api="IPN",
                      correlation_id = transactionId,
                      timestamp = date,
                      info = str(request.POST),
                      status=status,
                      transaction=transaction)
        
        return HttpResponse("Complete")
    
    except:
        traceback.print_exc()
        return HttpResponseForbidden()
        

def amazonPaymentReturn(request):
    '''
        This is the complete view called after the co-branded API completes.  It is called whenever the user
        approves a preapproval or a pledge.  This URL is set via the PAY api.
    '''
    try:
        
        # pick up all get and post parameters and display
        output = "payment complete"
        output += request.method + "\n" + str(request.REQUEST.items())
        
        signature = request.GET['signature']
        reference = request.GET['callerReference']
        token = request.GET['tokenID']
        status = request.GET['status']

        # BUGUBG - Should we verify the signature here?
        #
        # Find the transaction by reference, there should only be one
        # We will catch the exception if it does not exist
        #
        transaction = Transaction.objects.get(secret=reference)
        
        logging.info("Amazon Co-branded Return URL called for transaction id: %d" % transaction.id)
        logging.info(request.GET)
        
        #
        # BUGBUG, for now lets map amazon status code to paypal, just to keep things uninform
        #
        if transaction.type == PAYMENT_TYPE_INSTANT:
            # Instant payments need to be executed now
            
            # Log the authorize transaction
            r = PaymentResponse.objects.create(api="Authorize",
                          correlation_id = "None",
                          timestamp = str(datetime.datetime.now()),
                          info = str(request.GET),
                          status=status,
                          transaction=transaction)
            
            if status == AMAZON_STATUS_SUCCESS_ABT or status == AMAZON_STATUS_SUCCESS_ACH or status == AMAZON_STATUS_SUCCESS_CREDIT:
                # The above status code are unique to the return URL and are different than the pay API codes
                
                # Store the token, we need this for the IPN.
                transaction.pay_key = token
                
                #
                # BUGBUG, need to handle multiple recipients
                # Send the pay request now to ourselves
                #
                e = Execute(transaction=transaction)
                
                if e.success() and not e.error():
                    # Success case, save the ID.  Our IPN will update the status
                   print "Amazon Execute returned succesfully"
                   
                else:
                    logging.error("Amazon payment execution failed: ")
                    logging.error(e.envelope())
                    transaction.status = TRANSACTION_STATUS_ERROR

                # Log the pay transaction
                r = PaymentResponse.objects.create(api="Pay",
                          correlation_id = e.correlation_id(),
                          timestamp = e.timestamp(),
                          info = e.envelope(),
                          status = e.status,
                          transaction=transaction)
   
            else:
                # We may never see an IPN, set the status here
                logging.error("Amazon payment authorization failed: ")
                logging.error(request.GET)
                transaction.status = AMAZON_STATUS_FAILURE
            
                
        elif transaction.type == PAYMENT_TYPE_AUTHORIZATION:
            #
            # Future payments, we only need to store the token.  The authorization was requested with the default expiration
            # date set in our settings.  When we are ready, we can call execute on this
            #
            transaction.local_status = status
            
            if status == AMAZON_STATUS_SUCCESS_ABT or status == AMAZON_STATUS_SUCCESS_ACH or status == AMAZON_STATUS_SUCCESS_CREDIT:
                
                # The above status code are unique to the return URL and are different than the pay API codes
                transaction.status = TRANSACTION_STATUS_ACTIVE
                transaction.approved = True
                transaction.pay_key = token
                
            else:
                # We may never see an IPN, set the status here
                transaction.status = TRANSACTION_STATUS_ERROR
                
            # Log the trasaction
            r = PaymentResponse.objects.create(api="Authorize",
                          correlation_id = "None",
                          timestamp = str(datetime.datetime.now()),
                          info = str(request.GET),
                          status = status,
                          transaction=transaction)
                
        transaction.save()
        
        # Redirect to our pledge success URL
        return_path = "{0}?{1}".format(reverse('pledge_complete'), 
                                urllib.urlencode({'tid':transaction.id})) 
        return_url = urlparse.urljoin(settings.BASE_URL, return_path)
        return HttpResponseRedirect(return_url)

    except:
        logging.error("Amazon co-branded return-url FAILED with exception:")
        traceback.print_exc()
        
        cancel_path = "{0}?{1}".format(reverse('pledge_cancel'), 
                                urllib.urlencode({'tid':transaction.id}))            
        cancel_url = urlparse.urljoin(settings.BASE_URL, cancel_path)
            
        return HttpResponseRedirect(cancel_url)


class AmazonRequest:
    '''
       Handles common information that is processed from the response envelope of the amazon request.
        
    '''
    
    # Global values for the class
    response = None
    raw_response = None
    errorMessage = None
    status = None
    url = None
            
    def ack( self ):
        return None
        
    def success(self):
        
        if self.errorMessage:
            return False
        else:
            return True 
        
    def error(self):
        if self.errorMessage:
            return True
        else:
            return False
        
    def error_data(self):
        return None
    
    def error_id(self):
        return None
    
    def error_string(self):
        
        return self.errorMessage
    
    def envelope(self):
        
        # The envelope is used to store info about this request
        if self.response:
            return str(self.response)
        else:
            return None
      
    def correlation_id(self):
        # The correlation ID is unique to each API call
        if self.response:
            return self.response.TransactionId
        else:
            return None
        
    def timestamp(self):
        return str(datetime.datetime.now())
    
    
class Pay( AmazonRequest ):

  '''
    The pay function generates a redirect URL to approve the transaction
  '''
    
  def __init__( self, transaction, return_url=None, cancel_url=None, amount=None, paymentReason=""):
      
      try:
          logging.debug("Amazon PAY operation for transaction ID %d" % transaction.id)

          # Replace our return URL with a redirect through our internal URL
          self.original_return_url = return_url
          return_url = settings.BASE_URL + reverse('AmazonPaymentReturn')
            
          self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
          
          receiver_list = []
          receivers = transaction.receiver_set.all()
          
          if not amount:
              amount = 0
              for r in receivers:
                  amount += r.amount
                      
              logger.info(receiver_list)
              
          # Data fields for amazon
          
          expiry = now() + timedelta( days=settings.PREAPPROVAL_PERIOD )
          
          data = {
                  'amountType':'Maximum',  # The transaction amount is the maximum amount
                  'callerReference': transaction.secret,
                  'currencyCode': 'USD',
                  'globalAmountLimit': str(amount),
                  'validityExpiry': str(int(time.mktime(expiry.timetuple()))), # use the preapproval date by default
                  }
          
          self.url = self.connection.make_url(return_url, paymentReason, "MultiUse", str(amount), **data)
          
          logging.debug("Amazon PAY redirect url was: %s" % self.url)
          
      except FPSResponseError as (responseStatus, responseReason, body):
          logging.error("Amazon PAY api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
          logging.error(body)
          self.errorMessage = body
          
      except:
          logging.error("Amazon PAY FAILED with exception:")
          traceback.print_exc()
          self.errorMessage = "Error: Server Error"
      
  def api(self):
      return "Amazon Co-branded PAY request"
    
  def exec_status( self ):
      return None 
      
  def amount( self ):
      return None
      
  def key( self ):
      return None

  def next_url( self ):
      return self.url

  def embedded_url(self):
      return None
  
class Preapproval(Pay):
    
    def __init__( self, transaction, amount, expiry=None, return_url=None, cancel_url=None, paymentReason=""):
      
        # set the expiration date for the preapproval if not passed in.  This is what the paypal library does
        now_val = now()
        if expiry is None:
            expiry = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )
        transaction.date_authorized = now_val
        transaction.date_expired = expiry
        transaction.save()
          
        # Call into our parent class
        Pay.__init__(self, transaction, return_url=return_url, cancel_url=cancel_url, amount=amount, paymentReason=paymentReason)
  
  
class Execute(AmazonRequest):
    
    '''
        The Execute function sends an existing token(generated via the URL from the pay operation), and collects
        the money.
    '''
    
    def __init__(self, transaction=None):
        
        try:
            logging.debug("Amazon EXECUTE action for transaction id: %d" % transaction.id)
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
            self.transaction = transaction
            
            # BUGBUG, handle multiple receivers!  For now we just send the money to ourselves
            global_params = {"OverrideIPNURL": get_ipn_url()}
            self.raw_response = self.connection.pay(transaction.amount, 
                                              transaction.pay_key,
                                              recipientTokenId=None,
                                              callerReference=transaction.secret,
                                              senderReference=None,
                                              recipientReference=None,
                                              senderDescription=None,
                                              recipientDescription=None,
                                              callerDescription=None,
                                              metadata=None,
                                              transactionDate=None,
                                              reserve=False,
                                              extra_params=global_params)
          
            #
            # BUGBUG:
            # The boto FPS library throws an exception if an error is generated, we need to do a better
            # job of reporting the error when this occurs
            #
            
            self.response = self.raw_response[0]
            logging.debug("Amazon EXECUTE response for transaction id: %d" % transaction.id)
            logging.debug(str(self.response))
            
            self.status = self.response.TransactionStatus
            
            #
            # For amazon, the transactionID is per transaction, not per receiver.  For now we will store it in the preapproval key field
            # so we can use it to refund or get status later
            #
            transaction.preapproval_key = self.response.TransactionId 
            
            logging.debug("Amazon EXECUTE API returning with variables:")
            logging.debug(locals())
               
        except FPSResponseError as (responseStatus, responseReason, body):
            
            logging.error("Amazon EXECUTE api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
            logging.error(body)
            self.errorMessage = body
            
        except:
            logging.error("Amazon EXECUTE FAILED with exception:")
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
    def api(self):
        return "Amazon API Pay"
    
    def key(self):
        # IN paypal land, our key is updated from a preapproval to a pay key here, just return the existing key
        return self.transaction.pay_key
    
    

class Finish(AmazonRequest):
    '''
        The Finish function handles the secondary receiver in a chained payment.  Currently not implemented
        for amazon
    '''
    def __init__(self, transaction):
        
        try:
            
            print "Finish"
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"          
            
class PaymentDetails(AmazonRequest):
    '''
       Get details about executed PAY operation
       
       This api must set the following class variables to work with the code in manager.py
       
       status - one of the global transaction status codes
       transactions -- Not supported for amazon, used by paypal
       
    '''
    def __init__(self, transaction=None):
 
        try:
            logging.debug("Amazon PAYMENTDETAILS API for transaction id: %d" % transaction.id)
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
            self.transaction = transaction
            
            if not transaction.preapproval_key:
                # This is where we store the transaction ID
                self.errorMessage = "No Valid Transaction ID"
                return
            
            #
            # We need to reference the transaction ID here, this is stored in the preapproval_key as this
            # field is not used for amazon
            #
            self.raw_response = self.connection.get_transaction_status(transaction.preapproval_key)
            self.response = self.raw_response[0]
            
            logging.debug("Amazon PAYMENTDETAILS API for transaction id: %d returned response:")
            logging.debug(self.response)
            
            #
            # Now we need to build values to match the paypal response.
            # The two we need are status and and array of transactions.
            #
            
            # Check our status codes, note that these are different than the IPN status codes
            self.local_status = self.response.StatusCode
            self.message = self.response.StatusMessage
            
            
            if self.local_status == 'Canceled':
                self.status = TRANSACTION_STATUS_CANCELED
                
            elif self.local_status == 'Success':
                #
                # Note, there is a limitation here.  If the current status is refunded, this API will return "Success".
                # We must be careful to not overwrite refunded status codes.  There is no way that I can find to poll
                # to see if a transaction is refunded.  I need to investigate all of the data fields and see if we can find
                # that information
                #
                if transaction.status != TRANSACTION_STATUS_REFUNDED:
                    self.status = TRANSACTION_STATUS_COMPLETE
                else:
                    self.status = TRANSACTION_STATUS_REFUNDED
                    
            elif self.local_status == 'PendingNetworkResponse' or self.local_status == 'PendingVerification':
                self.status = TRANSACTION_STATUS_PENDING
            elif self.local_status == 'TransactionDenied':
                self.status = TRANSACTION_STATUS_FAILED
            else:
                self.status = TRANSACTION_STATUS_ERROR
            
            # Amazon does not support receivers at this point
            self.transactions = []
            
            logging.debug("Amazon PAYMENTDETAILS API returning with variables:")
            logging.debug(locals())
            
        except FPSResponseError as (responseStatus, responseReason, body):
            
            logging.error("Amazon PAYMENTDETAILS api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
            logging.error(body)
            self.errorMessage = body
              
        except:
            logging.error("Amazon PAYMENTDETAILS FAILED with exception:")
            self.errorMessage = "Error: ServerError"
            traceback.print_exc()
          
            

class CancelPreapproval(AmazonRequest):
    '''
        Cancels an exisiting token.  The current boto FPS library does not directly support
        the CancelToken API, just the Cancel API(for real money in-flight or reserved).
    '''
    
    def __init__(self, transaction):
        
        try:
            logging.debug("Amazon CANCELPREAPPROVAL api called for transaction id: %d" % transaction.id)
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
            self.transaction = transaction
            
            global_params = {"OverrideIPNURL": get_ipn_url()}
            params = global_params
            params['TokenId'] = transaction.pay_key
            params['ReasonText'] = "Cancel Reason"
        
            fps_response = self.connection.make_request("CancelToken", params)
            
            body = fps_response.read()

            if(fps_response.status == 200):
                
                rs = ResultSet()
                h = handler.XmlHandler(rs, self)
                xml.sax.parseString(body, h)
                
                if rs:
                    self.raw_response = rs
                    self.response = self.raw_response[0]
                    self.status = self.response.TransactionStatus
                    self.errorMessage = None
                
            else:
                #
                # Set an error message and failure status for 
                # our success() and error() functions
                #
                self.status = AMAZON_STATUS_FAILURE
                self.errorMessage = "%s - %s" % (fps_response.reason, body)
                
            logging.debug("Amazon CANCELPREAPPROVAL API returning with variables:")
            logging.debug(locals())
            
        except FPSResponseError as (responseStatus, responseReason, body):
            
            logging.error("Amazon CANCELPREAPPROVAL api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
            logging.error(body)
            self.errorMessage = body
            
        except:
            logging.error("Amazon CANCELPREAPPROVAL FAILED with exception:")
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class RefundPayment(AmazonRequest):
    
    def __init__(self, transaction):
        
        try:
            logging.debug("Amazon REFUNDPAYMENT API called for transaction id: %d", transaction.id)
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
            self.transaction = transaction
            
            if not transaction.preapproval_key:
                # This is where we store the transaction ID
                self.errorMessage = "No Valid Transaction ID"
                return
            
            #
            # We need to reference the transaction ID here, this is stored in the preapproval_key as this
            # field is not used for amazon
            #
            global_params = {"OverrideIPNURL": get_ipn_url()}
            self.raw_response = self.connection.refund(transaction.secret, transaction.preapproval_key, extra_params=global_params)
            self.response = self.raw_response[0]
            
            logging.debug("Amazon REFUNDPAYMENT response was:")
            logging.debug(str(self.response))
            
            self.status = self.response.TransactionStatus
            
            logging.debug("Amazon REFUNDPAYMENT API returning with variables:")
            logging.debug(locals())
            
        except FPSResponseError as (responseStatus, responseReason, body):
            
            logging.error("Amazon REFUNDPAYMENT api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
            logging.error(body)
            self.errorMessage = body
            
        except:
            logging.error("Amazon REFUNDPAYMENT FAILED with exception:")
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class PreapprovalDetails(AmazonRequest):
    '''
       Get details about an authorized token
       
       This api must set 4 different class variables to work with the code in manager.py
       
       status - one of the global transaction status codes
       approved - boolean value
       currency - not used in this API, but we can get some more info via other APIs - TODO
       amount - not used in this API, but we can get some more info via other APIs - TODO
       
    '''
    def __init__(self, transaction=None):
 
        try:
            logging.debug("Amazon PREAPPROVALDETAILS API called for transaction id: %d", transaction.id)
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(FPS_ACCESS_KEY, FPS_SECRET_KEY, host=settings.AMAZON_FPS_HOST)
            self.transaction = transaction
            
            
            #
            # We need to reference the caller reference here, we may not have a token if the return URL failed
            #
            self.raw_response = self.connection.get_token_by_caller_reference(transaction.secret)
            self.response = self.raw_response
            
            logging.debug("Amazon PREAPPROVALDETAILS response:")
            logging.debug(str(self.response))
    
            # 
            # Look for a token, we store this in the pay_key field
            #
            self.pay_key = self.response.TokenId
            self.local_status = self.response.TokenStatus
            
            # Possible status for the Token object are Active and Inactive
            if self.local_status == 'Active':
                self.status = TRANSACTION_STATUS_ACTIVE
                self.approved = True
            else:
                # It is not clear here if this should be failed or cancelled, but we have no way to know
                # the token is only active or now, so we will assume it is canceled.
                self.status = TRANSACTION_STATUS_CANCELED
                self.approved = False
                
            # Set the other fields that are expected.  We don't have values for these now, so just copy the transaction
            self.currency = transaction.currency
            self.amount = transaction.amount
            
            logging.debug("Amazon PREAPPROVALDETAILS API returning with variables:")
            logging.debug(locals())
            
        except FPSResponseError as (responseStatus, responseReason, body):
            
            logging.error("Amazon PREAPPROVALDETAILS api failed with status: %s, reason: %s and data:" % (responseStatus, responseReason))
            logging.error(body)
            self.errorMessage = body
              
        except:
            # If the boto API fails, it also throws an exception and we end up here
            logging.error("Amazon PREAPPROVALDETAILS FAILED with exception:")
            self.errorMessage = "Error: ServerError"
            traceback.print_exc()
        