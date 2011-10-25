import json
import logging
from xml.etree import ElementTree as ET
from requests import request
import oauth2 as oauth
from urlparse import urlparse, urlunparse, urljoin
from urllib import urlencode
import httplib
# import parse_qsl from cgi if it doesn't exist in urlparse
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

from django.conf import settings

logger = logging.getLogger(__name__)

# QUESTION: should the request_token, access_token be part of the state of the client?
# for simplicity for now, I will make them part of the state of GoodReadsClient

class GoodreadsException(Exception):
    pass

class GoodreadsAuthorizationRequired(GoodreadsException):
    pass

class GoodreadsClient(object):
    
    url = 'http://www.goodreads.com'
    request_token_url = urljoin(url,'oauth/request_token/')
    authorize_url = urljoin(url, '/oauth/authorize/')
    access_token_url = urljoin(url,'/oauth/access_token/')  
  
    def __init__(self,key,secret,access_token=None):
        self.key = key
        self.secret = secret
        self.consumer = oauth.Consumer(key=self.key,
                              secret=self.secret)
        
        self.client = oauth.Client(self.consumer)
        self.unauth_client = None
        
        if access_token is not None:
          self.__load_access_token(access_token)
        else:
          self.access_token = None
          
    @property     
    def is_authorized(self):
        return (self.access_token is not None)
    def begin_authorization (self, callback_url=None):
        # get request token
        response, content = self.client.request(GoodreadsClient.request_token_url, 'GET')
        
        if int(response['status']) != httplib.OK:
          raise Exception('Invalid response: %s' % response['status'])
        
        request_token = dict(parse_qsl(content))
        
        q = {'oauth_token':request_token['oauth_token']}
        if callback_url is not None:
          q['oauth_callback'] = callback_url
        
        authorize_link = GoodreadsClient.authorize_url + '?' + urlencode(q)
        return (authorize_link, request_token)
        
    def complete_authorization(self, request_token):
      token = oauth.Token(request_token['oauth_token'],
                          request_token['oauth_token_secret'])
      
      self.client = oauth.Client(self.consumer, token)
      response, content = self.client.request(GoodreadsClient.access_token_url, 'POST')
      if int(response['status']) != httplib.OK:
          raise Exception('Invalid response: %s' % response['status'])
      
      access_token_raw = dict(parse_qsl(content))
      self.__load_access_token(access_token_raw)
      return access_token_raw
      
    def __load_access_token(self, access_token):
        token = oauth.Token(access_token['oauth_token'],
                            access_token['oauth_token_secret'])
        self.access_token = token
        self.client = oauth.Client(self.consumer, self.access_token)        
  
    def __clear_access_token(self):
        self.access_token = None
        self.consumer = oauth.Consumer(key=self.key,
                              secret=self.secret)

    def auth_user(self):
        if self.is_authorized:
            response, content = self.client.request('%s/api/auth_user' % GoodreadsClient.url,
                                         'GET')
            if int(response['status']) != httplib.OK:
                raise GoodreadsException('Error authenticating Goodreads user: %s ' % response)
            else:
                doc = ET.fromstring(content)
                user = doc.find('user')
                userid = user.get('id')
                name = user.find('name').text
                link = user.find('link').text
                return({'userid':userid, 'name':name, 'link':link})
        else:
            raise GoodreadsAuthorizationRequired('Attempt to access auth_user without authorization.')
      
    def add_book(self, book_id=871441, shelf_name='to-read'):
      # the book is: "Moby-Dick: A Pop-Up Book" 871441
      body = urlencode({'name': 'to-read', 'book_id': book_id})
      headers = {'content-type': 'application/x-www-form-urlencoded'}
      response, content = self.client.request('%s/shelf/add_to_shelf.xml' % GoodreadsClient.url,
                                         'POST', body, headers)
      # check that the new resource has been created
      if int(response['status']) != httplib.CREATED:
          raise GoodreadsException('Cannot create resource: %s' % response['status'])
          logger.info('response,content: %s | %s ' % (response,content))
      else:
          return True
        
    def shelves_list(self,user_id,page=1):
        path = "/shelf/list.xml"
        params = {'user_id':user_id, 'page':page}
        params["key"] = self.key
        method = "GET"
        request_url = urljoin(GoodreadsClient.url, path)
        
        r = request(method,request_url,params=params)
        
        if r.status_code != httplib.OK:
            logger.info('headers, content: %s | %s ' % (r.headers,r.content))
            raise GoodreadsException('Error in shelves_list: %s %s ' % (r.headers, r.content))
        else:
            logger.info('headers, content: %s | %s ' % (r.headers,r.content))
            doc = ET.fromstring(r.content)
            shelves = doc.find('shelves')
            # do a simple parsing to a dictionary
            d = {k:int(shelves.attrib[k]) for k in shelves.attrib }
            d["user_shelves"] = [{'name':shelf.find('name').text,
                                  'book_count':int(shelf.find('book_count').text),
                                  'description':shelf.find('description').text if shelf.find('description').attrib['nil'] != 'true' else None } \
                for shelf in shelves.findall('user_shelf')]
            return d
        
        
    
