from regluit.payment.parameters import *
from regluit.payment.models import Transaction
from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.xmlutils import SimplerXMLGenerator
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template import RequestContext

import datetime
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


# transaction_type constants
IPN_TYPE_PAYMENT = 'Adaptive Payment PAY'
IPN_TYPE_ADJUSTMENT = 'Adjustment'
IPN_TYPE_PREAPPROVAL = 'Adaptive Payment Preapproval'

#status constants
IPN_STATUS_CREATED = 'CREATED'
IPN_STATUS_COMPLETED = 'COMPLETED'
IPN_STATUS_INCOMPLETE = 'INCOMPLETE'
IPN_STATUS_ERROR = 'ERROR'
IPN_STATUS_REVERSALERROR = 'REVERSALERROR'
IPN_STATUS_PROCESSING = 'PROCESSING'
IPN_STATUS_PENDING = 'PENDING'

# action_type constants
IPN_ACTION_TYPE_PAY = 'PAY'
IPN_ACTION_TYPE_CREATE = 'CREATE'

# individual sender transaction constants
IPN_TXN_STATUS_COMPLETED = 'Completed'
IPN_TXN_STATUS_PENDING = 'Pending'
IPN_TXN_STATUS_REFUNDED = 'Refunded'

IPN_REASON_CODE_CHARGEBACK = 'Chargeback'
IPN_REASON_CODE_SETTLEMENT = 'Settlement'
IPN_REASON_CODE_ADMIN_REVERSAL = 'Admin reversal'
IPN_REASON_CODE_REFUND = 'Refund'


class url_request( object ): 

  def __init__( self, base, url, data=None, headers={} ):
   
    conn = httplib.HTTPSConnection(base)
    conn.request("POST", url, data, headers)
    
    #Check the response - should be 200 OK.
    self.response = conn.getresponse()

  def content( self ):
    return self.response.read()

  def code( self ):
    return self.response.status


class Pay( object ):
  def __init__( self, transaction, receiver_list):
      
      headers = {
            'X-PAYPAL-SECURITY-USERID':PAYPAL_USERNAME, 
            'X-PAYPAL-SECURITY-PASSWORD':PAYPAL_PASSWORD, 
            'X-PAYPAL-SECURITY-SIGNATURE':PAYPAL_SIGNATURE,
            'X-PAYPAL-APPLICATION-ID':PAYPAL_APPID,
            'X-PAYPAL-REQUEST-DATA-FORMAT':'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
            }

      return_url = BASE_URL + COMPLETE_URL
      cancel_url = BASE_URL + CANCEL_URL
      print "Return URL: " + return_url
      print "Cancel URL: " + cancel_url
      
      data = {
              'currencyCode': transaction.currency,
              'returnUrl': return_url,
              'cancelUrl': cancel_url,
              'requestEnvelope': { 'errorLanguage': 'en_US' },
              } 

      data['actionType'] = 'PAY'
      data['receiverList'] = { 'receiver': receiver_list }

      data['ipnNotificationUrl'] = BASE_URL + 'paypalipn'

      self.raw_request = json.dumps(data)
   
      self.raw_response = url_request( PAYPAL_ENDPOINT, "/AdaptivePayments/Pay", data=self.raw_request, headers=headers ).content() 
      print "paypal PAY response was: %s" % self.raw_response
      self.response = json.loads( self.raw_response )
      print self.response
    
  def status( self ):
      if self.response.has_key( 'paymentExecStatus' ):
          return self.response['paymentExecStatus']
      else:
          return None 
  
  def error( self ):
      if self.response.has_key('error'):
          error = self.response['error']
          print error
          return error[0]['message']
      else:
          return None
      
  def amount( self ):
    return decimal.Decimal(self.results[ 'payment_gross' ])
  
  def paykey( self ):
    return self.response['payKey']

  def next_url( self ):
    return '%s?cmd=_ap-payment&paykey=%s' % ( PAYPAL_PAYMENT_HOST, self.response['payKey'] )


class IPN( object ):
    
  def __init__( self, request ):
      
    try:
        # verify that the request is paypal's
        self.error = None
    
        url = "%s?cmd=_notify-validate" % PAYPAL_PAYMENT_HOST
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
  
        # check payment status
        if request.POST['status'] != 'COMPLETED':
            self.error = 'PayPal status was "%s"' % request.get('status')
            return

        # Process the details
        self.status = request.POST.get('status', None)
        self.sender_email = request.POST.get('sender_email', None)
        self.action_type = request.POST.get('action_type', None)
        self.key = request.POST.get('pay_key', None)
        self.transaction_type = request.POST.get('transaction_type', None)
        
        self.process_transactions(request)
        
    except:
        self.error = "Error: ServerError"
        traceback.print_exc()

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
              print transdict
                
        
