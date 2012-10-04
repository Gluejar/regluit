from regluit.payment.models import  PaymentResponse

from django.http import  HttpResponseForbidden
from datetime import timedelta
from regluit.utils.localdatetime import now, zuluformat

import datetime
import time


class BasePaymentRequest:
    '''
       Handles common information incident to payment processing
        
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
        return None
        
    def timestamp(self):
        return str(datetime.datetime.now())
    
class Processor:
    """a function that returns for the given payment processor"""
    requires_explicit_preapprovals=False
    
    def make_account(self, user, token):
        """template function for return a payment.Account corresponding to the payment system"""
        return None
    
    def ProcessIPN(self, request):
        return HttpResponseForbidden()
        
  
    class Pay( BasePaymentRequest ):
    
      '''
        The pay function generates a redirect URL to approve the transaction
      '''
        
      def __init__( self, transaction, return_url=None,  amount=None, paymentReason=""):
          self.transaction=transaction
          
      def api(self):
          return "null api"
        
      def exec_status( self ):
          return None 
          
      def amount( self ):
          return None
          
      def key( self ):
          return None
    
      def next_url( self ):
          return self.url
      
    class Preapproval(Pay):
        
        def __init__( self, transaction, amount, expiry=None, return_url=None,  paymentReason=""):
          
            # set the expiration date for the preapproval if not passed in.  This is what the paypal library does
            now_val = now()
            if expiry is None:
                expiry = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )
            transaction.date_authorized = now_val
            transaction.date_expired = expiry
            transaction.save()
              
            # Call into our parent class
            Pay.__init__(self, transaction, return_url=return_url,  amount=amount, paymentReason=paymentReason)
      
      
    class Execute(BasePaymentRequest):
        
        '''
            The Execute function sends an existing token(generated via the URL from the pay operation), and collects
            the money.
        '''
        
        def __init__(self, transaction=None):
            self.transaction = transaction
                
        def api(self):
            return "Base Pay"
        
        def key(self):
            # IN paypal land, our key is updated from a preapproval to a pay key here, just return the existing key
            return self.transaction.pay_key
        
        
    
    class Finish(BasePaymentRequest):
        '''
            The Finish function handles the secondary receiver in a chained payment.  
        '''
        def __init__(self, transaction):
            
            print "Finish"
                
                
    class PaymentDetails(BasePaymentRequest):
        '''
           Get details about executed PAY operation
           
           This api must set the following class variables to work with the code in manager.py
           
           status - one of the global transaction status codes
           transactions -- Not supported for amazon, used by paypal
           
        '''
        def __init__(self, transaction=None):
            self.transaction = transaction
              
                
    
    class CancelPreapproval(BasePaymentRequest):
        '''
            Cancels an exisiting token.  
        '''
        
        def __init__(self, transaction):
            self.transaction = transaction
                
                
    class RefundPayment(BasePaymentRequest):
        
        def __init__(self, transaction):
            self.transaction = transaction
                
                
    
                
                
    class PreapprovalDetails(BasePaymentRequest):
        '''
           Get details about an authorized token
           
           This api must set 4 different class variables to work with the code in manager.py
           
           status - one of the global transaction status codes
           approved - boolean value
           currency - not used in this API, but we can get some more info via other APIs - TODO
           amount - not used in this API, but we can get some more info via other APIs - TODO
           
        '''
        def __init__(self, transaction=None):
            self.transaction = transaction
            