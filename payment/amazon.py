from regluit.payment.parameters import *
from django.core.urlresolvers import reverse
from django.conf import settings
from regluit.payment.models import Transaction
from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.xmlutils import SimplerXMLGenerator
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from boto.fps.connection import FPSConnection

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

class AmazonRequest:
    '''
       Handles common information that is processed from the response envelope of the amazon request.
        
    '''
    
    # Global values for the class
    response = None
    raw_response = None
    errorMessage = None
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
        return None
      
    def correlation_id(self):
        return None
        
    def timestamp(self):
        return None
        

class Pay( AmazonRequest ):
  def __init__( self, transaction, return_url=None, cancel_url=None, options=None):
      
      try:
          
          if not options:
              options = {}
              
          # Use the boto class top open a connection
          self.connection = FPSConnection(settings.FPS_ACCESS_KEY, settings.FPS_SECRET_KEY, **options)
          
          receiver_list = []
          receivers = transaction.receiver_set.all()
          
          if len(receivers) == 0:
              raise Exception
          
          # by setting primary_string of the first receiver to 'true', we are doing a Chained payment
          total_amount = 0
          for r in receivers:
              total_amount += r.amount
                      
          logger.info(receiver_list)
              
          # Data fields for amazon
          data = {} 
          
          print "Amazon PURCHASE url request data: %s" % data
          
          self.url = self.connection.make_url(return_url, "Test Payment", "SingleUse", str(total_amount), **data)
          print "Amazon PURCHASE url was: %s" % self.url
          
      except:
          traceback.print_exc()
          self.errorMessage = "Error: Server Error"
      
  def api(self):
      return None
    
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
  