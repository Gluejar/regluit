from wepay import WePay

# should load the keys for WePay from db -- but for now just hardcode here

try:
    from regluit.core.models import Key
    WEPAY_ACCESS_TOKEN = Key.objects.get(name="WEPAY_ACCESS_TOKEN").value
    WEPAY_CLIENT_SECRET = Key.objects.get(name="WEPAY_CLIENT_SECRET").value
    WEPAY_ACCOUNT_ID = Key.objects.get(name="WEPAY_ACCOUNT_ID").value
    logger.info('Successful loading of WEPAY_*_KEYs')
except Exception, e:
    WEPAY_ACCESS_TOKEN = 'a680cfd2b814ef0e4938b865c96879136a74970ad6c9425e8c98de50b40007af'
    WEPAY_CLIENT_SECRET= 'f9bf05cd50'
    WEPAY_ACCOUNT_ID = 1226963

# set production to True for live environments
PRODUCTION = False
wepay = WePay(PRODUCTION, WEPAY_ACCESS_TOKEN)

# collect credit card and do a delay charge to gluejar -- then to LR....

# Then, you can charge customers on their behalf. It?s just like charging a customer normally, except you should use their access_token and account_id instead of your own.

def create_checkout(amount, description, account_id=WEPAY_ACCOUNT_ID, mode="iframe", type='GOODS'):
    
    # type: one of GOODS, SERVICE, PERSONAL, or DONATION
    # create the checkout
    response = wepay.call('/checkout/create', {
        'account_id': WEPAY_ACCOUNT_ID,
        'amount': amount,
        'short_description': description,
        'type': type,
        'mode': mode
    })
    
    # display the response
    return response
