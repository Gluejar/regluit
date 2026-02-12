"""
external library imports
"""
import logging
import os
import re
import time
import unittest
from urlparse import (urlparse, urlunparse)

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""
django imports
"""
import django
from django.conf import settings


def set_attribute_value(sel, elem_id, value):
    sel.execute_script("""document.getElementById("{elem_id}").value="{value}";""".format(elem_id=elem_id, 
                                                                        value=value))
    return sel

def find_element_by_css_selector(sel, selector, wait_time=10):
    return WebDriverWait(sel,wait_time).until(lambda d: d.find_element_by_css_selector(selector))

def find_elements_by_css_selector(sel, selector, wait_time=10):
    return WebDriverWait(sel,wait_time).until(lambda d: d.find_elements_by_css_selector(selector))

def wait_until_url(sel, url, wait_time=10):
    return WebDriverWait(sel,wait_time).until(lambda d: d.current_url == url)

def setup_selenium():
    # Set the display window for our xvfb
    os.environ['DISPLAY'] = ':99'

def selenium_driver(browser='firefox'):

    if browser == 'firefox':
        firefox_capabilities = DesiredCapabilities.FIREFOX
        #firefox_capabilities['marionette'] = True
        firefox_capabilities['binary'] = settings.FIREFOX_PATH
        driver = webdriver.Firefox(capabilities=firefox_capabilities)
    elif browser == 'htmlunit':
        # HTMLUNIT with JS -- not successful
        driver = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)
    elif browser == 'phantomjs':
        driver = webdriver.PhantomJS()
    # chrome
    else:
        driver = webdriver.Chrome(executable_path=settings.CHROMEDRIVER_PATH)

    return driver

def test_login (unglue_it_url = settings.LIVE_SERVER_TEST_URL, do_local=True, backend='amazon', browser='firefox'):

    UNGLUE_IT_URL = unglue_it_url
    USER = settings.UNGLUEIT_TEST_USER
    PASSWORD = settings.UNGLUEIT_TEST_PASSWORD
    
    setup_selenium()
    
    sel = selenium_driver(browser=browser)

    time.sleep(5)
    
    print "now opening unglue.it"
    
    #sel.get("http://www.google.com")
    sel.get(UNGLUE_IT_URL)    
    
    # long wait because sel is slow after PayPal
    sign_in_link = WebDriverWait(sel, 100).until(lambda d : d.find_element_by_xpath("//span[contains(text(),'Sign In')]/.."))
    sign_in_link.click()

    # enter unglue.it login info
    #input_username = WebDriverWait(sel,20).until(lambda d : d.find_element_by_css_selector("input#id_username"))
    input_username = find_element_by_css_selector(sel,"input#id_username")
    input_username.send_keys(USER)
    sel.find_element_by_css_selector("input#id_password").send_keys(PASSWORD)
    sel.find_element_by_css_selector("input[value*='Sign in with Password']").click()    
    
    yield sel

def test_donate(sel):

    donate_button = find_element_by_css_selector(sel,"input[id='donatesubmit']")
    donate_amount = find_element_by_css_selector(sel,"input[id='amount']")
        
    # set to 12.34
    set_attribute_value(sel, 'amount', '12.34')
    
    donate_button.click()

    # check we're at /payment/fund/?

    path = urlparse(sel.current_url).path.strip().split('/')
    assert path[1:3] == [u'payment', u'fund']

    # set donation form 

    set_attribute_value(sel, 'card_Number', '4242424242424242')
    set_attribute_value(sel, 'card_CVC', '888')
    set_attribute_value(sel, 'card_ExpiryMonth', '12')
    set_attribute_value(sel, 'card_ExpiryYear', '2020')
    set_attribute_value(sel, 'card_Name', 'Raymond Yee')
    set_attribute_value(sel, 'card_AddressState', 'CA')
    set_attribute_value(sel, 'card_AddressZip', '94706')
    set_attribute_value(sel, 'card_AddressCountry', 'United States')

    submit_button = find_element_by_css_selector(sel,"input[id='cc_submit']")
    submit_button.click()

    # did the donation go through ok?

    trans_summary = find_element_by_css_selector(sel, "div[class='trans_summary']")
    assert "This amount has been charged to your credit card." in trans_summary.text

    path = urlparse(sel.current_url).path.strip().split('/')
    assert path[1:3] == [u'fund', u'complete']

    return sel
