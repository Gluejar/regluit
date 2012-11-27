PAYMENT_TYPE_NONE = 0
PAYMENT_TYPE_INSTANT = 1
PAYMENT_TYPE_AUTHORIZATION = 2

PAYMENT_HOST_NONE = "none"
PAYMENT_HOST_PAYPAL = "paypal"
PAYMENT_HOST_AMAZON = "amazon"
PAYMENT_HOST_STRIPE = "stripelib"

PAYMENT_HOST_TEST = "test"
PAYMENT_HOST_CREDIT = "credit"

EXECUTE_TYPE_NONE = 0
EXECUTE_TYPE_CHAINED_INSTANT = 1
EXECUTE_TYPE_CHAINED_DELAYED = 2
EXECUTE_TYPE_PARALLEL = 3

# The default status for a transaction that is newly created
TRANSACTION_STATUS_NONE = 'None'

# Indicates a transaction has been sent to the co-branded API
TRANSACTION_STATUS_CREATED = 'Created'

# A general complete code to indicate payment is complete to all receivers
TRANSACTION_STATUS_COMPLETE = 'Complete'

# A general pending code that means in process
TRANSACTION_STATUS_PENDING = 'Pending'

# This means that the max amount has increased but the increase hasn't been executed
TRANSACTION_STATUS_MODIFIED = 'Modified'

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

# Transaction written off -- unable to successfully be charged after campaign succeeded 
TRANSACTION_STATUS_WRITTEN_OFF = 'Written-Off'
