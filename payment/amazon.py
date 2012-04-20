from regluit.payment.parameters import *
from django.core.urlresolvers import reverse
from django.conf import settings
from regluit.payment.models import Transaction, PaymentResponse
from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.xmlutils import SimplerXMLGenerator
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from boto.fps.connection import FPSConnection
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponseBadRequest
from datetime import timedelta
from regluit.utils.localdatetime import now, zuluformat
import dateutil

import dateutil.parser
import hashlib
import httplib
import traceback
import datetime
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

AMAZON_STATUS_CANCELLED = 'Cancelled'
AMAZON_STATUS_FAILURE = 'Failure'
AMAZON_STATUS_PENDING = 'Pending'
AMAZON_STATUS_RESERVED = 'Reserved'
AMAZON_STATUS_SUCCESS = 'Success'

AMAZON_IPN_STATUS_CANCELLED = 'CANCELLED'
AMAZON_IPN_STATUS_FAILURE = 'FAILURE'
AMAZON_IPN_STATUS_PENDING = 'PENDING'
AMAZON_IPN_STATUS_RESERVED = 'RESERVED'
AMAZON_IPN_STATUS_SUCCESS = 'SUCCESS'


def ProcessIPN(request):
    '''
        IPN handler for amazon
    '''
    try:
        print "Process Amazon IPN"
    except:
        traceback.print_exc()
        
        

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
                
                # Store the token
                transaction.pay_key = token
                
                #
                # BUGBUG, need to handle multiple recipients
                # Send the pay request now to ourselves
                #
                e = Execute(transaction=transaction)
                
                transaction.local_status = e.status
                
                if e.status == AMAZON_STATUS_SUCCESS:
                    transaction.status = TRANSACTION_STATUS_COMPLETE_PRIMARY
                    
                elif e.status == AMAZON_STATUS_PENDING:
                    # Amazon leaves CC transactions pending until we get the IPN
                    transaction.status = TRANSACTION_STATUS_PENDING
                    
                else:
                    transaction.status = TRANSACTION_STATUS_ERROR
                
                if e.success() and not e.error():
                    # Success case, save the ID
                   print "Amazon Execute returned succesfully"
                else:
                    print "Amazon Execute returned an error, status %s" % e.status
                    # Failure case

                # Log the pay transaction
                r = PaymentResponse.objects.create(api="Pay",
                          correlation_id = e.correlation_id(),
                          timestamp = e.timestamp(),
                          info = e.envelope(),
                          status = e.status,
                          transaction=transaction)
   
            else:
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
        if self.status:
            #
            # process the boto response if we have one.  The status codes here are only boto response codes, not
            # return_url codes
            #  
            if self.status == AMAZON_STATUS_SUCCESS or self.status == AMAZON_STATUS_PENDING:
                return True
            else:
                return False
            
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
          
            print "Amazon EXECUTE response was: %s" % self.raw_response
            
            self.response = self.raw_response[0]
            print "RESPONSE: %s" % self.response
            self.status = self.response.TransactionStatus
            print "STATUS: %s" % self.status
          
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
    def api(self):
        return "Amazon API Pay"
    
    def key(self):
        # IN paypal land, our key is updated from a preapproval to a pay key here, just return the existing key
        return self.transaction.pay_key

class Finish(AmazonRequest):
    
    def __init__(self, transaction):
        
        try:
            
            print "Finish"
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"          
            
class PaymentDetails(AmazonRequest):
  def __init__(self, transaction=None):
 
      try:
         print "Payment Details"
              
      except:
          self.errorMessage = "Error: ServerError"
          traceback.print_exc()
          
            

class CancelPreapproval(AmazonRequest):
    
    def __init__(self, transaction):
        
        try:
            
            print "Cancel Preapproval"
            
        except:
            traceback.print_exc()
            self.errorMessage = "Error: Server Error"
            
            
class RefundPayment(AmazonRequest):
    
    def __init__(self, transaction):
        
        try:
            print "Refund Payment"
            
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
        