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
import xml.sax

import traceback
import datetime
import logging
import urlparse
import time

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


def ProcessIPN(request):
    '''
        IPN handler for amazon.  Here is a litle background on amazon IPNS
        
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
        print "Process Amazon IPN"
        
        uri = request.build_absolute_uri()
        parsed_url = urlparse.urlparse(uri)
        
        connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY)
        
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
        
        print "Amazon IPN POST DATA:"
        print request.POST

        reference = request.POST['callerReference']
        type = request.POST['notificationType']
        
        # In the case of cancelling a token, there is no transaction, so this info is not set
        transactionId = request.POST.get('transactionId', None)
        date = request.POST.get('transactionDate', None)
        operation = request.POST.get('operation', None)
        
        # We should always find the transaction by the token
        transaction = Transaction.objects.get(secret=reference)
        
        if type == AMAZON_NOTIFICATION_TYPE_STATUS:
            
            status = request.POST['transactionStatus']
            # status update for the token, save the actual value
            transaction.local_status = status
            
            # Now map our local status to the global status codes
            if operation == AMAZON_OPERATION_TYPE_PAY:
               
                
                if status == AMAZON_IPN_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_COMPLETE_PRIMARY
                    
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
                    transaction.status = TRANSACTION_STATUS_COMPLETE_PRIMARY
                else:
                    transaction.status = TRANSACTION_STATUS_ERROR
                    
            elif operation == AMAZON_OPERATION_TYPE_CANCEL:
                
                if status == AMAZON_IPN_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_COMPLETE_PRIMARY
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
        approves a preapproval or a pledge.
    '''
    try:
        
        # pick up all get and post parameters and display
        output = "payment complete"
        output += request.method + "\n" + str(request.REQUEST.items())
        print output
        
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
        return HttpResponse("Success")

    except:
        traceback.print_exc()
        return HttpResponseBadRequest("Error")


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
        
        print "CALLING SUCCESS"
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
    
  def __init__( self, transaction, return_url=None, cancel_url=None, options=None, amount=None):
      
      try:
          
          if not options:
              options = {}
              
          # Use the boto class top open a connection
          self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY, **options)
          
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
          
          print "Amazon PURCHASE url request data: %s" % data
          
          self.url = self.connection.make_url(return_url, "Test Payment", "MultiUse", str(amount), **data)
          
          print "Amazon PURCHASE url was: %s" % self.url
          
      except:
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
    
  def __init__( self, transaction, amount, expiry=None, return_url=None, cancel_url=None):
      
      # Call into our parent class
      Pay.__init__(self, transaction, return_url=return_url, cancel_url=cancel_url, options=None, amount=amount)
  
  
class Execute(AmazonRequest):
    
    '''
        The Execute function sends an existing token(generated via the URL from the pay operation), and collects
        the money.
    '''
    
    def __init__(self, transaction=None):
        
        try:
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY)
            self.transaction = transaction
            
            # BUGBUG, handle multiple receivers!  For now we just send the money to ourselves
              
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
                                              reserve=False)
          
            #
            # BUGBUG:
            # The boto FPS library throws an exception if an error is generated, we need to do a better
            # job of reporting the error when this occurs
            #
            
            print "Amazon EXECUTE response was: %s" % self.raw_response
            self.response = self.raw_response[0]
            print "RESPONSE: %s" % self.response
            self.status = self.response.TransactionStatus
            print "STATUS: %s" % self.status
            
            #
            # For amazon, the transactionID is per transaction, not per receiver.  For now we will store it in the preapproval key field
            # so we can use it to refund or get status later
            #
            transaction.preapproval_key = self.response.TransactionId    
          
        except:
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
    
    def __init__(self, transaction=None):
 
        try:
          
            # Use the boto class top open a connection
            self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY)
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
            
            print "Amazon TRANSACTION STATUS response was: %s" % self.raw_response
              
            self.response = self.raw_response[0]
            print "RESPONSE: %s" % self.response
    
            
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
                self.status = TRANSACTION_STATUS_COMPLETE_PRIMARY
            elif self.local_status == 'PendingNetworkResponse' or self.local_status == 'PendingVerification':
                self.status = TRANSACTION_STATUS_PENDING
            elif self.local_status == 'TransactionDenied':
                self.status = TRANSACTION_STATUS_FAILED
            else:
                self.status = TRANSACTION_STATUS_ERROR
            
            # Amazon does not support receivers at this point
            self.transactions = []
            
            print self.status
              
        except:
            self.errorMessage = "Error: ServerError"
            traceback.print_exc()
          
            

class CancelPreapproval(AmazonRequest):
    '''
        Cancels an exisiting token.  The current boto FPS library does not directly support
        the CancelToken API, just the Cancel API(for real money in-flight or reserved).
    '''
    
    def __init__(self, transaction):
        
        try:
            
            # Use the boto class top open a connection
            self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY)
            self.transaction = transaction
            
            params = {}
            params['TokenId'] = transaction.pay_key
            params['ReasonText'] = "Cancel Reason"
        
            fps_response = self.connection.make_request("CancelToken", params)
            
            body = fps_response.read()
            print body
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
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class RefundPayment(AmazonRequest):
    
    def __init__(self, transaction):
        
        try:
            # Use the boto class top open a connection
            self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY)
            self.transaction = transaction
            
            if not transaction.preapproval_key:
                # This is where we store the transaction ID
                self.errorMessage = "No Valid Transaction ID"
                return
            
            #
            # We need to reference the transaction ID here, this is stored in the preapproval_key as this
            # field is not used for amazon
            #
            self.raw_response = self.connection.refund(transaction.secret, transaction.preapproval_key)
            
            print "Amazon TRANSACTION REFUND response was: %s" % self.raw_response
              
            self.response = self.raw_response[0]
            print "RESPONSE: %s" % self.response
            self.status = self.response.TransactionStatus
            print "STATUS: %s" % self.status
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class PreapprovalDetails(AmazonRequest):
  def __init__(self, transaction):
 
      try:
          print "Preapproval Details"
          
      except:
          self.errorMessage = "Error: ServerError"
          traceback.print_exc()
        