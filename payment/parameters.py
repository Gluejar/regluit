PAYMENT_TYPE_NONE = 0
PAYMENT_TYPE_INSTANT = 1
PAYMENT_TYPE_AUTHORIZATION = 2

PAYMENT_HOST_NONE = "none"
PAYMENT_HOST_PAYPAL = "paypal"
PAYMENT_HOST_AMAZON = "amazon"

EXECUTE_TYPE_NONE = 0
EXECUTE_TYPE_CHAINED_INSTANT = 1
EXECUTE_TYPE_CHAINED_DELAYED = 2
EXECUTE_TYPE_PARALLEL = 3

TARGET_TYPE_NONE = 0
TARGET_TYPE_CAMPAIGN = 1
TARGET_TYPE_LIST = 2
TARGET_TYPE_DONATION = 3

# The default status for a transaction that is newly created
TRANSACTION_STATUS_NONE = 'None'

# Indicates a transaction has been sent to the co-branded API
TRANSACTION_STATUS_CREATED = 'Created'

# A general complete code to indicate payment is comlete to all receivers
TRANSACTION_STATUS_COMPLETE = 'Complete'

# A general pending code that means in process
TRANSACTION_STATUS_PENDING = 'Pending'


# Indicates a preapproval is active
TRANSACTION_STATUS_ACTIVE = 'Active'

# Only used in paypal at the moment, indicates payment was made to only 1 of multiple receivers
TRANSACTION_STATUS_INCOMPLETE = 'Incomplete'

# A general error code, see provider specific info for more detils
TRANSACTION_STATUS_ERROR = 'Error'

# A preapproval was canceled
TRANSACTION_STATUS_CANCELED = 'Canceled'

# Money that was transfered was refunded, either through a reversal or manual refund
TRANSACTION_STATUS_REFUNDED = 'Refunded'

# The transaction was refused/denied
TRANSACTION_STATUS_FAILED = 'Failed'

# these two following parameters are probably extraneous since I think we will compute dynamically where to return each time.
COMPLETE_URL = '/paymentcomplete'
NEVERMIND_URL = '/paymentnevermind'
