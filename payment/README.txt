
Setup instructions for payment module

1)  In parameters.py, set the following:

    PAYPAL_USERNAME = Paypal username from developer.paypal.com
    PAYPAL_PASSWORD =  Paypal password from developer.paypal.com
    PAYPAL_SIGNATURE = Paypal signature from developer.paypal.com
    PAYPAL_APPID = 'APP-80W284485P519543T' (for all sandbox apps), or the real APPID

    BASE_URL = Set this to the server IP address that is accessible via port 80.  
                Local IP addresses, or non-port 80 addresses will NOT work with paypal IPN.
                
    COMPLETE_URL = relative local URL for a plege confirmation
    CANCEL_URL = relative local url for a pledge cacellation
    
2) Sync the database to include the payment specific tables

3) Configure your paypal sandbox account at developer.paypal.com with at least 1 seller and 1 buyer.  The buyer info is entered into the sandbox, the seller
    info needs to be entered into the pledge/payment itself

4) A test pledge code sample is available in regluit.payment.view.testPledge
