from regluit.payment.parameters import *
from django.core.urlresolvers import reverse
from django.conf import settings
from regluit.payment.models import Transaction, Receiver
from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.xmlutils import SimplerXMLGenerator
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template import RequestContext

from datetime import timedelta
from regluit.utils.localdatetime import now, zuluformat
import dateutil

import dateutil.parser
import hashlib
import httplib
import traceback
import uuid
import os
import urllib
import urllib2
import logging
import random
import commands
import smtplib
import urlparse
import decimal
import sys

logger = logging.getLogger(__name__)

# transaction_type constants
IPN_TYPE_PAYMENT = 'Adaptive Payment PAY'
IPN_TYPE_ADJUSTMENT = 'Adjustment'
IPN_TYPE_PREAPPROVAL = 'Adaptive Payment PREAPPROVAL'

#pay API status constants
#  NONE' is not something the API produces but is particular to our implementation
IPN_PAY_STATUS_NONE = 'NONE'


#The following apply to INSTANT PAYMENTS
#https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_APPayAPI
#CREATED - The payment request was received; funds will be transferred once the payment is approved
#COMPLETED - The payment was successful
#INCOMPLETE - Some transfers succeeded and some failed for a parallel payment or, for a delayed chained payment, secondary receivers have not been paid
#ERROR - The payment failed and all attempted transfers failed or all completed transfers were successfully reversed
#REVERSALERROR - One or more transfers failed when attempting to reverse a payment
#PROCESSING - The payment is in progress
#PENDING - The payment is awaiting processing

IPN_PAY_STATUS_CREATED = 'CREATED'
IPN_PAY_STATUS_COMPLETED = 'COMPLETED'
IPN_PAY_STATUS_INCOMPLETE = 'INCOMPLETE'
IPN_PAY_STATUS_ERROR = 'ERROR'
IPN_PAY_STATUS_REVERSALERROR = 'REVERSALERROR'
IPN_PAY_STATUS_PROCESSING = 'PROCESSING'
IPN_PAY_STATUS_PENDING = 'PENDING'

# particular to preapprovals
# https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_APPreapprovalDetails
#ACTIVE - The preapproval is active
#CANCELED - The preapproval was explicitly canceled by the sender or by PayPal
#DEACTIVED - The preapproval is not active; you can be reactivate it by resetting the personal identification number (PIN) or by contacting PayPal

IPN_PREAPPROVAL_STATUS_ACTIVE = "ACTIVE"
IPN_PREAPPROVAL_STATUS_CANCELED = "CANCELED"
IPN_PREAPPROVAL_STATUS_DEACTIVED = "DEACTIVED"

# https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_APIPN
#COMPLETED - The sender's transaction has completed
#PENDING - The transaction is awaiting further processing
#CREATED - The payment request was received; funds will be transferred once approval is received
#PARTIALLY_REFUNDED - Transaction was partially refunded
#DENIED - The transaction was rejected by the receiver
#PROCESSING - The transaction is in progress
#REVERSED - The payment was returned to the sender
#REFUNDED - The payment was refunded
#FAILED - The payment failed

IPN_SENDER_STATUS_COMPLETED = 'COMPLETED'
IPN_SENDER_STATUS_PENDING = 'PENDING'
IPN_SENDER_STATUS_CREATED = 'CREATED'
IPN_SENDER_STATUS_PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED'
IPN_SENDER_STATUS_DENIED = 'DENIED'
IPN_SENDER_STATUS_PROCESSING = 'PROCESSING'
IPN_SENDER_STATUS_REVERSED = 'REVERSED'
IPN_SENDER_STATUS_REFUNDED = 'REFUNDED'
IPN_SENDER_STATUS_FAILED = 'FAILED'

# action_type constants
IPN_ACTION_TYPE_PAY = 'PAY'
IPN_ACTION_TYPE_CREATE = 'CREATE'

# individual sender transaction constants (???)
IPN_TXN_STATUS_COMPLETED = 'Completed'
IPN_TXN_STATUS_PENDING = 'Pending'
IPN_TXN_STATUS_REFUNDED = 'Refunded'

# adaptive payment adjusted IPN reason codes
IPN_REASON_CODE_CHARGEBACK_SETTLEMENT = 'Chargeback Settlement'
IPN_REASON_CODE_ADMIN_REVERSAL = 'Admin reversal'
IPN_REASON_CODE_REFUND = 'Refund'

def PaypalStatusToGlobalStatus(status):
    '''
        This represents the default mapping of paypal status codes to global status codes
        There are cases where this mapping will not apply and the individual API calls must do
        additional processing
    '''
    
    if status == IPN_PAY_STATUS_CREATED:
        return TRANSACTION_STATUS_CREATED
    
    elif status == IPN_PAY_STATUS_COMPLETED:
        return TRANSACTION_STATUS_COMPLETE
    
    elif status == IPN_PAY_STATUS_INCOMPLETE:
        return TRANSACTION_STATUS_INCOMPLETE
    
    elif status == IPN_PAY_STATUS_ERROR:
        return TRANSACTION_STATUS_ERROR
    
    elif status == IPN_PAY_STATUS_REVERSALERROR:
        return TRANSACTION_STATUS_ERROR
    
    elif status == IPN_PAY_STATUS_PROCESSING:
        return TRANSACTION_STATUS_PENDING
    
    elif status == IPN_PAY_STATUS_PENDING:
        return TRANSACTION_STATUS_PENDING
    
    elif status == IPN_PREAPPROVAL_STATUS_ACTIVE:
        return TRANSACTION_STATUS_ACTIVE
    
    elif status == IPN_PREAPPROVAL_STATUS_CANCELED:
        return TRANSACTION_STATUS_CANCELED
    
    elif status == IPN_PREAPPROVAL_STATUS_DEACTIVED:
        return TRANSACTION_STATUS_CANCELED
    
    elif status == IPN_SENDER_STATUS_COMPLETED:
        return TRANSACTION_STATUS_COMPLETE
    
    elif status == IPN_SENDER_STATUS_PENDING:
        return TRANSACTION_STATUS_CPENDING
    
    elif status == IPN_SENDER_STATUS_CREATED:
        return TRANSACTION_STATUS_CREATED
    
    elif status == IPN_SENDER_STATUS_PARTIALLY_REFUNDED:
        return TRANSACTION_STATUS_REFUNDED
    
    elif status == IPN_SENDER_STATUS_DENIED:
        return TRANSACTION_STATUS_FAILED
    
    elif status == IPN_SENDER_STATUS_PROCESSING:
        return TRANSACTION_STATUS_PENDING
    
    elif status == IPN_SENDER_STATUS_REVERSED:
        return TRANSACTION_STATUS_REFUNDED
    
    elif status == IPN_SENDER_STATUS_REFUNDED:
        return TRANSACTION_STATUS_REFUNDED
    
    elif status == IPN_SENDER_STATUS_FAILED:
        return TRANSACTION_STATUS_FAILED
    
    else:
        return TRANSACTION_STATUS_ERRROR
    
    
def ProcessIPN(request):
    '''
    processIPN
    
    Turns a request from Paypal into an IPN, and extracts info.   We support 2 types of IPNs:
    
    1) Payment - Used for instant payments and to execute pre-approved payments
    2) Preapproval - Used for comfirmation of a preapproval
    
    '''        
    try:
        ipn = IPN(request)
    
        if ipn.success():
            logger.info("Valid IPN")
            logger.info("IPN Transaction Type: %s" % ipn.transaction_type)
            
            if ipn.transaction_type == IPN_TYPE_PAYMENT:
                # payment IPN. we use our unique reference for the transaction as the key
                # is only valid for 3 hours
                
                uniqueID = ipn.uniqueID()
                t = Transaction.objects.get(secret=uniqueID)
                
                # The local_status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                t.local_status = ipn.status
                t.status  = PaypalStatusToGlobalStatus(ipn.status)
                
                for item in ipn.transactions:
                    
                    try:
                        r = Receiver.objects.get(transaction=t, email=item['receiver'])
                        logger.info(item)
                        # one of the IPN_SENDER_STATUS codes defined in paypal.py,  If we are doing delayed chained
                        # payments, then there is no status or id for non-primary receivers.  Leave their status alone
                        r.status = item['status_for_sender_txn']
                        r.txn_id = item['id_for_sender_txn']
                        r.save()
                    except:
                        # Log an exception if we have a receiver that is not found.  This will be hit
                        # for delayed chained payments as there is no status or id for the non-primary receivers yet
                        traceback.print_exc()
                
                t.save()
                
                logger.info("Final transaction status: %s" % t.status)
                
            elif ipn.transaction_type == IPN_TYPE_ADJUSTMENT:
                # a chargeback, reversal or refund for an existng payment

                uniqueID = ipn.uniqueID()
                if uniqueID:
                    t = Transaction.objects.get(secret=uniqueID)
                else:
                    key = ipn.pay_key
                    t = Transaction.objects.get(pay_key=key)
                
                # The status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                t.local_status = ipn.status
                t.status  = PaypalStatusToGlobalStatus(ipn.status)
                
                # Reason code indicates more details of the adjustment type
                t.reason = ipn.reason_code
    
                # Update the receiver status codes
                for item in ipn.transactions:
                    
                    try:
                        r = Receiver.objects.get(transaction=t, email=item['receiver'])
                        logger.info(item)
                        # one of the IPN_SENDER_STATUS codes defined in paypal.py,  If we are doing delayed chained
                        # payments, then there is no status or id for non-primary receivers.  Leave their status alone
                        r.status = item['status_for_sender_txn']
                        r.save()
                    except:
                        # Log an exception if we have a receiver that is not found.  This will be hit
                        # for delayed chained payments as there is no status or id for the non-primary receivers yet
                        traceback.print_exc()
                        
                t.save()                    
                
                    
            elif ipn.transaction_type == IPN_TYPE_PREAPPROVAL:
                
                # IPN for preapproval always uses the key to ref the transaction as this is always valid
                key = ipn.preapproval_key
                t = Transaction.objects.get(preapproval_key=key)
                
                # The status is always one of the IPN_PREAPPROVAL_STATUS codes defined in paypal.py
                t.local_status = ipn.status
                t.status  = PaypalStatusToGlobalStatus(ipn.status)
                
                # capture whether the transaction has been approved
                t.approved = ipn.approved
                
                t.save()
                logger.info("IPN: Preapproval transaction: " + str(t.id) + " Status: " + ipn.status)
                    
            else:
                logger.info("IPN: Unknown Transaction Type: " + ipn.transaction_type)
            
            
        else:
            logger.info("ERROR: INVALID IPN")
            logger.info(ipn.error)
    
    except:
        traceback.print_exc()
        

class PaypalError(RuntimeError):
    pass

class url_request( object ): 

  def __init__( self, request):
   
    conn = httplib.HTTPSConnection(settings.PAYPAL_ENDPOINT)
    conn.request("POST", request.url, request.raw_request, request.headers)
    
    #Check the response - should be 200 OK.
    self.response = conn.getresponse()

  def content( self ):
    return self.response.read()

  def code( self ):
    return self.response.status

class PaypalEnvelopeRequest:
    '''
       Handles common information that is processed from the response envelope of the paypal request.
       
       All of our requests have a response envelope of the following format:
       
      ack common:AckCode
        Acknowledgement code. It is one of the following values:
            Success - The operation completed successfully.
            Failure - The operation failed.
            Warning - Warning.
            SuccessWithWarning - The operation completed successfully; however, there is a warning message.
            FailureWithWarning - The operation failed with a warning message.
        build Build number; it is used only by Developer Technical Support.
        correlationId Correlation ID; it is used only by Developer Technical Support.
        timestamp Date on which the response was sent. The time is currently not supported.

        Additionally, our subclasses may set the error_message field if an undetermined error occurs.  Examples of undertmined errors are:
            HTTP error codes(not 200)
            Invalid parameters
            Python exceptions during processing
            
        All clients should check both the success() and the error() functions to determine the result of the operation
        
    '''
    
    # Global values for the class
    response = None
    raw_response = None
    errorMessage = None
    raw_request = None
    url = None
            
    def ack( self ):
            
        if self.response and self.response.has_key( 'responseEnvelope' ) and self.response['responseEnvelope'].has_key( 'ack' ):
            return self.response['responseEnvelope']['ack']
        else:
            return None
        
    def success(self):
        status = self.ack()

        # print status
        if status == "Success" or status == "SuccessWithWarning":
            return True
        else:
            return False 
        
    def error(self):
        message = self.errorMessage
        # print message
        if message:
            return True
        else:
            return False
        
    def error_data(self):
        
        if self.response and self.response.has_key('error'):
            return self.response['error']
        else:
            return None
    
    def error_id(self):
        
        if self.response and self.response.has_key('error'):
            return self.response['error'][0]['errorId']
        else:
            return None
    
    def error_string(self):
                
        if self.response and self.response.has_key('error'):
            return self.response['error'][0]['message']
      
        elif self.errorMessage:
            return self.errorMessage
      
        else:
            return None
    
    def envelope(self):

        if self.response and self.response.has_key('responseEnvelope'):
            return self.response['responseEnvelope']
        else:
            return None
      
    def correlation_id(self):
        if self.response and self.response.has_key('responseEnvelope') and self.response['responseEnvelope'].has_key('correlationId'):
            return self.response['responseEnvelope']['correlationId']
        else:
            return None
        
    def timestamp(self):
        if self.response and self.response.has_key('responseEnvelope') and self.response['responseEnvelope'].has_key('timestamp'):
            return self.response['responseEnvelope']['timestamp']
        else:
            return None
    
class Pay( PaypalEnvelopeRequest ):
  def __init__( self, transaction, return_url=None, nevermind_url=None, paymentReason=""):
      
      #BUGBUG: though I'm passing in paymentReason (to make it signature compatible with Amazon, it's not being wired in properly yet)
      try:
          
          headers = {
                'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
                }
    
          if return_url is None:
              return_url = settings.BASE_URL + COMPLETE_URL
          if nevermind_url is None:
              nevermind_url = settings.BASE_URL + nevermind_url
            
          logger.info("Return URL: " + return_url)
          logger.info("Cancel URL: " + nevermind_url)
          
          receiver_list = []
          receivers = transaction.receiver_set.all()
          
          if len(receivers) == 0:
              raise Exception
          
          # by setting primary_string of the first receiver to 'true', we are doing a Chained payment
          for r in receivers:
              if len(receivers) > 1:
                  if r.primary and (transaction.execution == EXECUTE_TYPE_CHAINED_INSTANT or transaction.execution == EXECUTE_TYPE_CHAINED_DELAYED):
                      # Only set a primary if we are using chained payments
                      primary_string = 'true'
                  else:
                      primary_string = 'false'
                      
                  receiver_list.append({'email':r.email,'amount':str(r.amount), 'primary':primary_string})
              else:
                  receiver_list.append({'email':r.email,'amount':str(r.amount)})
                      
          logger.info(receiver_list)
            
          # actionType can be 'PAY', 'CREATE', or 'PAY_PRIMARY'
          # PAY_PRIMARY': "For chained payments only, specify this value to delay payments to the secondary receivers; only the payment to the primary receiver is processed"
          
          if transaction.execution == EXECUTE_TYPE_CHAINED_DELAYED:
              self.actionType = 'PAY_PRIMARY'
          else:
              self.actionType = 'PAY'
          
          # feesPayer: SENDER, PRIMARYRECEIVER, EACHRECEIVER, SECONDARYONLY
          # The PayPal documentation says that fees for delayed chain payments cannot be set to secondaryonly
          # but the sandbox seems to show the secondary recipient paying all the fees.
          # if only one receiver, set to EACHRECEIVER, otherwise set to SECONDARYONLY
          
          if len(receivers) == 1:
            feesPayer = 'EACHRECEIVER'
          else:
            feesPayer = 'SECONDARYONLY'
          
          data = {
                  'actionType': self.actionType,
                  'receiverList': { 'receiver': receiver_list },
                  'currencyCode': transaction.currency,
                  'returnUrl': return_url,
                  'cancelUrl': nevermind_url,
                  'requestEnvelope': { 'errorLanguage': 'en_US' },
                  'ipnNotificationUrl': settings.BASE_URL + reverse('HandleIPN', args=["paypal"]),
                  'feesPayer': feesPayer,
                  'trackingId': transaction.secret
                  } 
          
          logging.info("paypal PAY data: %s" % data)
          #print >> sys.stderr, "paypal PAY data:", data
          # Is ipnNotificationUrl being computed properly
          #print >> sys.stderr, 'ipnNotificationUrl', settings.BASE_URL + reverse('PayPalIPN')
          
          # a Pay operation can be for a payment that goes through immediately or for setting up a preapproval.
          # transaction.reference is not null if it represents a preapproved payment, which has a preapprovalKey.
          if transaction.preapproval_key:
              data['preapprovalKey'] = transaction.preapproval_key
          
          self.raw_request = json.dumps(data)
          self.url = "/AdaptivePayments/Pay"
          self.headers = headers
          self.connection = url_request(self)
          self.code = self.connection.code()
          
          if self.code != 200:
              self.errorMessage = 'PayPal response code was %i' % self.code
              return
          
          self.raw_response = self.connection.content() 
          #print >> sys.stderr, "PAY request", settings.PAYPAL_ENDPOINT, "/AdaptivePayments/Pay", self.raw_request, headers 
          logger.info("paypal PAY response was: %s" % self.raw_response)
          #print >> sys.stderr, "paypal PAY response was:", self.raw_response
          self.response = json.loads( self.raw_response )
          logger.info(self.response)
          
      except:
          traceback.print_exc()
          self.errorMessage = "Error: Server Error"
      
  def api(self):
      return self.actionType
    
  def exec_status( self ):
      if self.response.has_key( 'paymentExecStatus' ):
          return self.response['paymentExecStatus']
      else:
          return None 
      
  def amount( self ):
      if self.response.has_key('payment_gross'):
          return self.response['payment_gross']
      else:
          return None
      
  def key( self ):
      if self.response.has_key('payKey'):
          return self.response['payKey']
      else:
          return None

  def next_url( self ):
    return '%s?cmd=_ap-payment&paykey=%s' % (settings.PAYPAL_PAYMENT_HOST, self.response['payKey'] )

  def embedded_url(self):
      return '%s/webapps/adaptivepayment/flow/pay?paykey=%s&expType=light'  % ( settings.PAYPAL_PAYMENT_HOST, self.response['payKey'] )
  
  
class Execute(Pay):
    '''
        For payapl, execute is the same as pay.  The pay funciton detects whether an execute or a co-branded operation
        is called for.
    '''
    def __init__(self, transaction, return_url=None, nevermind_url=None):
        # Call our super class.  In python 2.2+, we can't use super here, so just call init directly
        Pay.__init__(self, transaction, return_url, nevermind_url)
    
class Finish(PaypalEnvelopeRequest):
    
    def __init__(self, transaction=None):
        
        try:
            
            self.errorMessage = None
            self.response = None
            
            headers = {
            'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
            'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
            'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
            'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
            'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
            }
            
            
            if transaction.execution != EXECUTE_TYPE_CHAINED_DELAYED:
                self.errorMessage = "Invalid transaction type for execution"
                return
            
            if not transaction.pay_key:
                self.errorMessage = "No Paykey Found in transaction"
                return
             
            data = {
                      'payKey': transaction.pay_key,
                      'requestEnvelope': { 'errorLanguage': 'en_US' }
                   } 
      
            logging.info("paypal EXECUTE data: %s" % data)
            self.raw_request = json.dumps(data)
            self.url = "/AdaptivePayments/ExecutePayment"
            self.headers = headers
            self.connection = url_request(self)
            self.code = self.connection.code()
            
            if self.code != 200:
                self.errorMessage = 'PayPal response code was %i' % self.code
                return
            
            self.raw_response = self.connection.content()
                        
            logger.info("paypal EXECUTE response was: %s" % self.raw_response)
            self.response = json.loads( self.raw_response )
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server error occurred"
            

class PaymentDetails(PaypalEnvelopeRequest):
    
  '''
       Get details about executed PAY operation
       
       This api must set the following class variables to work with the code in manager.py
       
       status - one of the global transaction status codes
       transactions -- A list of all receiver transactions associated with this payment
           status -  the status of the receiver transaction
           txn_id -  the id of the receiver transaction
       
  '''
    
  def __init__(self, transaction=None):
 
      try:
          self.transaction = transaction
          
          headers = {
                'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
                }
          
          # we can feed any of payKey, transactionId, and trackingId to identify transaction in question
          # I think we've been tracking payKey.  We might want to use our own trackingId (what's Transaction.secret for?)  
          data = {
                  'requestEnvelope': { 'errorLanguage': 'en_US' },
                  'trackingId':transaction.secret
                  }       
    
          self.raw_request = json.dumps(data)
          self.headers = headers
          self.url = "/AdaptivePayments/PaymentDetails"
          self.connection = url_request(self)
          
          self.code = self.connection.code()
          
          if self.code != 200:
            self.errorMessage = 'PayPal response code was %i' % self.code
            return
        
          self.raw_response = self.connection.content()
          
          logger.info("paypal PaymentDetails response was: %s" % self.raw_response)
          self.response = json.loads( self.raw_response )
          logger.info(self.response)
          
          self.local_status = self.response.get("status", None)
          self.status = PaypalStatusToGlobalStatus(self.local_status)
          
          self.trackingId = self.response.get("trackingId", None)
          self.feesPayer = self.response.get("feesPayer", None)
          payment_info_list = self.response.get("paymentInfoList", None)
          payment_info = payment_info_list.get("paymentInfo", None)
          
          self.transactions = []
          for payment in payment_info:
              receiver = {}
              receiver['status'] = payment.get("transactionStatus", None)
              receiver['txn_id'] = payment.get("transactionId")
              
              r = payment.get("receiver", None)
              if r:
                  receiver['email'] = r.get('email')
    
                  
              self.transactions.append(receiver)
              
      except:
          self.errorMessage = "Error: ServerError"
          traceback.print_exc()
          
              
  def compare(self):
    """compare current status information from what's in the current transaction object"""
    # I don't think we do anything with fundingtypeList, memo
    # status can be: 
    # transaction.type should be PAYMENT_TYPE_INSTANT
    # actionType can be: 'PAY', 'CREATE', 'PAY_PRIMARY' -- I think we are doing only 'PAY' right now

    comp = [(self.transaction.status, self.response.get('status')),
            (self.transaction.type, self.response.get('actionType')),
            (self.transaction.currency, self.response.get('currencyCode')),
            ('EACHRECEIVER' if len(self.transaction.receiver_set.all()) == 1 else 'SECONDARYONLY',self.response.get('feesPayer')),
            (self.transaction.reference, self.response.get('payKey')),  # payKey supposedly expires after 3 hours
            ('false', self.response.get('reverseAllParallelPaymentsOnError')),
            (None, self.response.get('sender'))
            ]
    
    # loop through recipients
    
    return comp
    
    # also getting sender / senderEmail info too here that we don't currently hold in transaction.  Want to save?  Does that info come in IPN?
    # responseEnvelope
    
    # reverseAllParallelPaymentsOnError
    # self.response.get('responseEnvelope')['ack'] should be 'Success' Can also be 'Failure', 'Warning', 'SuccessWithWarning', 'FailureWithWarning'
    # can possibly use self.response.get('responseEnvelope')['timestamp'] to update self.transaction.date_modified
    # preapprovalKey -- self.transaction doesn't hold that info right now
    # paymentInfoList -- holds info for each recipient
    

class CancelPreapproval(PaypalEnvelopeRequest):
    
    def __init__(self, transaction):
        
        try:
            
            headers = {
                     'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                     'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                     'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                     'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                     'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                     'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON',
                     }
          
            data = {
                  'preapprovalKey':transaction.preapproval_key,
                  'requestEnvelope': { 'errorLanguage': 'en_US' }
                  } 
    
            self.raw_request = json.dumps(data)
            self.headers = headers
            self.url = "/AdaptivePayments/CancelPreapproval"
            self.connection = url_request(self)
            self.code = self.connection.code()
            
            if self.code != 200:
                self.errorMessage = 'PayPal response code was %i' % self.code
                return
            
            self.raw_response = self.connection.content() 
            logger.info("paypal CANCEL PREAPPROBAL response was: %s" % self.raw_response)
            self.response = json.loads( self.raw_response )
            logger.info(self.response)
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class RefundPayment(PaypalEnvelopeRequest):
    
    def __init__(self, transaction):
        
        try:
            
            headers = {
                     'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                     'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                     'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                     'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                     'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                     'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON',
                     }
          
            data = {
                  'payKey':transaction.pay_key,
                  'requestEnvelope': { 'errorLanguage': 'en_US' }
                  } 
    
            self.raw_request = json.dumps(data)
            self.headers = headers
            self.url = "/AdaptivePayments/Refund"
            self.connection = url_request(self)
            self.code = self.connection.code()
            
            if self.code != 200:
                self.errorMessage = 'PayPal response code was %i' % self.code
                return
            
            self.raw_response = self.connection.content() 
            logger.info("paypal Refund response was: %s" % self.raw_response)
            self.response = json.loads( self.raw_response )
            logger.info(self.response)
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
        

class Preapproval( PaypalEnvelopeRequest ):
  def __init__( self, transaction, amount, expiry=None, return_url=None, nevermind_url=None, paymentReason=""):
      
      # BUGBUG:  though I'm passing in paymentReason (to make it signature compatible with Amazon, it's not being wired in properly yet)
      
      try:
          
          headers = {
                     'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                     'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                     'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                     'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                     'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                     'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON',
                     }
    
          if return_url is None:
            return_url = settings.BASE_URL + COMPLETE_URL
          if nevermind_url is None:
            nevermind_url = settings.BASE_URL + NEVERMIND_URL
          
          # set the expiration date for the preapproval if not passed in
          now_val = now()
          if expiry is None:
            expiry = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )
          transaction.date_authorized = now_val
          transaction.date_expired = expiry
          transaction.save()
          
          data = {
                  'endingDate': zuluformat(expiry),
                  'startingDate': zuluformat(now_val),
                  'maxTotalAmountOfAllPayments': '%.2f' % transaction.amount,
                  'maxNumberOfPayments':1,
                  'maxAmountPerPayment': '%.2f' % transaction.amount,
                  'currencyCode': transaction.currency,
                  'returnUrl': return_url,
                  'cancelUrl': nevermind_url,
                  'requestEnvelope': { 'errorLanguage': 'en_US' },
                  'ipnNotificationUrl': settings.BASE_URL + reverse('HandleIPN', args=["paypal"])
                  }
    
          # Is ipnNotificationUrl being computed properly
          # print >> sys.stderr, 'ipnNotificationUrl', settings.BASE_URL + reverse('PayPalIPN')
          
          self.raw_request = json.dumps(data)
          self.url = "/AdaptivePayments/Preapproval"
          self.headers = headers
          self.connection = url_request(self)
          self.code = self.connection.code()
          
          if self.code != 200:
            self.errorMessage = 'PayPal response code was %i' % self.code
            return
        
          self.raw_response = self.connection.content() 
          logger.info("paypal PREAPPROVAL response was: %s" % self.raw_response)
          # print >> sys.stderr, "paypal PREAPPROVAL response was:", self.raw_response
          self.response = json.loads( self.raw_response )
          logger.info(self.response)
          
      except:
          traceback.print_exc()
          self.errorMessage = "Error: Server Error Occurred"
          
  def key( self ):
    if self.response.has_key( 'preapprovalKey' ):
      return self.response['preapprovalKey']
    else:
      return None
  
  def next_url( self ):
    return '%s?cmd=_ap-preapproval&preapprovalkey=%s' % ( settings.PAYPAL_PAYMENT_HOST, self.response['preapprovalKey'] )


class PreapprovalDetails(PaypalEnvelopeRequest):
    
  '''
       Get details about an authorized token
       
       This api must set 4 different class variables to work with the code in manager.py
       
       status - one of the global transaction status codes
       approved - boolean value
       currency - 
       amount - 

  '''
    
  def __init__(self, transaction):
 
      try:
          self.transaction = transaction
          
          headers = {
                'X-PAYPAL-SECURITY-USERID':settings.PAYPAL_USERNAME, 
                'X-PAYPAL-SECURITY-PASSWORD':settings.PAYPAL_PASSWORD, 
                'X-PAYPAL-SECURITY-SIGNATURE':settings.PAYPAL_SIGNATURE,
                'X-PAYPAL-APPLICATION-ID':settings.PAYPAL_APPID,
                'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
                'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
                }
          
          # we can feed any of payKey, transactionId, and trackingId to identify transaction in question
          # I think we've been tracking payKey.  We might want to use our own trackingId (what's Transaction.secret for?)  
          data = {
                  'requestEnvelope': { 'errorLanguage': 'en_US' },
                  'preapprovalKey':transaction.preapproval_key
                  }       
    
          self.raw_request = json.dumps(data)
          self.headers = headers
          self.url = "/AdaptivePayments/PreapprovalDetails"
          self.connection = url_request(self)
          self.code = self.connection.code()
          
          if self.code != 200:
            self.errorMessage = 'PayPal response code was %i' % self.code
            return
          
          self.raw_response = self.connection.content() 
          logger.info("paypal PreapprovalDetails response was: %s" % self.raw_response)
          self.response = json.loads( self.raw_response )
          logger.info(self.response)
          
          self.local_status = self.response.get("status", None)
          self.status = PaypalStatusToGlobalStatus(self.local_status)
          
          self.amount = self.response.get("maxTotalAmountOfAllPayments", None)
          self.currency = self.response.get("currencyCode", None)
          
          # a bit uncertain about how well PayPal sticks to a standard case
          approved = self.response.get("approved", 'None')    
          if approved.lower() == 'true':
            self.approved = True
          elif approved.lower() == 'false':
            self.approved = False
          else:
            self.approved = None

          try:
            self.expiration = dateutil.parser.parse(self.response.get("endingDate"))
          except:
            self.expiration = None
          
          try:
            self.date = dateutil.parser.parse(self.response.get("startingDate", None))
          except:
            self.date = None
          
      except:
          self.errorMessage = "Error: ServerError"
          traceback.print_exc()
      

class IPN( object ):
    
  def __init__( self, request ):
      
    try:
        # verify that the request is paypal's
        self.error = None
    
        url = "%s?cmd=_notify-validate" % settings.PAYPAL_PAYMENT_HOST
        data=urllib.urlencode(request.POST.copy())
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        raw_response = response.read()
        status = response.code

        # check code
        if status != 200:
            self.error = 'PayPal response code was %i' % verify_response.code()
            return
  
        # check response
        if raw_response != 'VERIFIED':
            self.error = 'PayPal response was "%s"' % raw_response
            return

        # Process the details
        self.status = request.POST.get('status', None)
        self.sender_email = request.POST.get('sender_email', None)
        self.action_type = request.POST.get('action_type', None)
        self.pay_key = request.POST.get('pay_key', None)
        self.preapproval_key = request.POST.get('preapproval_key', None)
        self.transaction_type = request.POST.get('transaction_type', None)
        self.reason_code = request.POST.get('reason_code', None)
        self.trackingId = request.POST.get('tracking_id', None)
        
        # a bit uncertain about how well PayPal sticks to a standard case
        approved = request.POST.get("approved", 'None')    
        if approved.lower() == 'true':
          self.approved = True
        elif approved.lower() == 'false':
          self.approved = False
        else:
          self.approved = None        
        
        self.process_transactions(request)
        
    except:
        self.error = "Error: ServerError"
        traceback.print_exc()

  def uniqueID(self):
      
      if self.trackingId:
          return self.trackingId
      else:
          return None
      
        
  def success( self ):
    return self.error == None

    
  @classmethod
  def slicedict(cls, d, s):
      return dict((str(k.replace(s, '', 1)), v) for k,v in d.iteritems() if k.startswith(s)) 
        
  def process_transactions(self, request):
      
      self.transactions = []
      
      transaction_nums = range(6)
      for transaction_num in transaction_nums:
          transdict = IPN.slicedict(request.POST, 'transaction[%s].' % transaction_num)
          if len(transdict) > 0:
              self.transactions.append(transdict)
              logger.info(transdict)
                


        
